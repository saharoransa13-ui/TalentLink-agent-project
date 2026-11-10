
import os
from types import SimpleNamespace

from backend.rag.answerer import answer_question


class FakePipeline:
    def __init__(self, chunks):
        self.chunks = chunks
        self.calls = []

    def retrieve(self, question, top_k=4):
        self.calls.append((question, top_k))
        return self.chunks


def make_chunk(
    text="Windows Server supports centralized administration.",
    source="IT_Guide.pdf",
    chunk_index=2,
    similarity=0.91,
):
    return SimpleNamespace(
        text=text,
        source=source,
        file_type="pdf",
        chunk_index=chunk_index,
        similarity=similarity,
    )


def test_answer_includes_retrieved_source_citations(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    pipeline = FakePipeline([make_chunk()])

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": "Windows Server supports centralized administration [S1]."
                        }
                    }
                ]
            }

    def fake_post(url, **kwargs):
        assert url == "https://example.com/v1/chat/completions"
        assert "Windows Server supports centralized administration." in (
            kwargs["json"]["messages"][1]["content"]
        )
        return FakeResponse()

    monkeypatch.setattr("backend.rag.answerer.requests.post", fake_post)

    result = answer_question(pipeline, "What does Windows Server support?")

    assert result["llm_status"] == "success"
    assert "[S1]" in result["answer"]
    assert result["citations"][0]["source"] == "IT_Guide.pdf"
    assert result["citations"][0]["chunk_index"] == 2
    assert pipeline.calls == [("What does Windows Server support?", 4)]


def test_no_chunks_does_not_call_llm(monkeypatch):
    pipeline = FakePipeline([])

    def unexpected_post(*args, **kwargs):
        raise AssertionError("LLM must not be called without retrieved chunks")

    monkeypatch.setattr("backend.rag.answerer.requests.post", unexpected_post)

    result = answer_question(pipeline, "Unknown topic")

    assert result["llm_status"] == "not_needed"
    assert result["citations"] == []
    assert "couldn't find relevant information" in result["answer"]


def test_llm_failure_returns_safe_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    pipeline = FakePipeline([make_chunk()])

    def failing_post(*args, **kwargs):
        raise __import__("requests").ConnectionError("simulated failure")

    monkeypatch.setattr("backend.rag.answerer.requests.post", failing_post)

    result = answer_question(pipeline, "What does the guide say?")

    assert result["llm_status"] == "error"
    assert result["citations"][0]["source"] == "IT_Guide.pdf"
    assert "couldn't generate a grounded answer" in result["answer"]


def test_empty_question_is_rejected():
    pipeline = FakePipeline([make_chunk()])

    try:
        answer_question(pipeline, "   ")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("An empty question should raise ValueError")


def test_top_k_must_be_in_range():
    pipeline = FakePipeline([])

    try:
        answer_question(pipeline, "A question", top_k=11)
    except ValueError as exc:
        assert "top_k must be between 1 and 10" in str(exc)
    else:
        raise AssertionError("Invalid top_k should raise ValueError")
