import json
import os

from dotenv import load_dotenv
from groq import Groq

from cv_schema import CVProfile
from pii import redact_pii

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"

SYSTEM = """You read CVs and reply with JSON only.
Rules:
- Extract only what is written in the CV. Never guess or add anything.
- If something is not written, use null (or [] for a list).
- Keep the wording of each skill as written, but one skill per item:
  "Excel (pivot tables, VLOOKUP)" becomes "Excel", "pivot tables", "VLOOKUP".
- skills_used of a job or a project: only skills NAMED in that job's or project's own text.
  Do not infer: DAX does not mean Power BI unless "Power BI" is written there.
- Your JSON must match this JSON schema:
"""


def read_cv_with_llm(cv_text: str) -> CVProfile:
    safe_text = redact_pii(cv_text)                        # 1. no personal data leaves the PC
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM + json.dumps(CVProfile.model_json_schema())},
            {"role": "user", "content": safe_text},
        ],
        response_format={"type": "json_object"},           # 2. the reply must be valid JSON
        temperature=0,
        reasoning_effort="low",
    )
    print("Tokens in:", response.usage.prompt_tokens, "out:", response.usage.completion_tokens)
    reply = response.choices[0].message.content
    return CVProfile.model_validate_json(reply)
    print(reply)                                  # see the raw JSON once, for learning
