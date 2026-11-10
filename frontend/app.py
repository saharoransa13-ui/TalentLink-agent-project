import json
import os
import requests
import streamlit as st

from translations import TEXTS

st.set_page_config(page_title="CV Gap Analysis", page_icon="🧭", layout="wide")
API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

# --- Language selection ---
LANG_OPTIONS = {"English": "en", "العربية": "ar"}
lang_label = st.sidebar.radio("🌐 Language / اللغة", list(LANG_OPTIONS.keys()), horizontal=True)
LANG = LANG_OPTIONS[lang_label]


def t(key, **kwargs):
    """Return the UI text for the current language (falls back to English)."""
    entry = TEXTS.get(key, {})
    text = entry.get(LANG) or entry.get("en") or key
    return text.format(**kwargs) if kwargs else text


# Right-to-left layout for Arabic.
if LANG == "ar":
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"], [data-testid="stSidebar"] { direction: rtl; }
        [data-testid="stMarkdownContainer"] { text-align: right; }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title(t("title"))
st.caption(t("subtitle"))
try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    health.raise_for_status()
    roles_resp = requests.get(f"{API_URL}/roles", timeout=5)
    roles_resp.raise_for_status()
    roles = roles_resp.json()
except Exception as exc:
    st.error(t("api_unreachable"))
    with st.expander(t("technical_details")):
        st.code(f"{API_URL}\n{exc}\n\npython -m uvicorn backend.main:app --reload")
    st.stop()

role_map = {r["title"]: r["role_id"] for r in roles}
with st.form("analyze_form"):
    uploaded = st.file_uploader(t("upload_cv"), type=["pdf", "docx", "txt"])
    selected_title = st.selectbox(t("target_role"), list(role_map.keys()))
    submitted = st.form_submit_button(t("analyze_button"), type="primary")

if submitted:
    if uploaded is None:
        st.warning(t("upload_first"))
        st.stop()
    with st.spinner(t("analyzing")):
        try:
            response = requests.post(
                f"{API_URL}/analyze",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
                data={"role_id": role_map[selected_title]},
                timeout=90
            )
            if response.status_code != 200:
                try:
                    reason = response.json().get("detail", response.text)
                except ValueError:
                    reason = response.text
                st.error(t("analysis_failed", reason=reason))
                st.stop()
            report = response.json()
            st.session_state["report"] = report
        except requests.RequestException:
            st.error(t("connection_failed"))
            st.stop()

with st.expander("Live job and course discovery (optional)"):
    st.caption("Uses configured provider APIs. Add API credentials to the backend .env file to enable live results.")
    search_query = st.text_input("Search topic / role", placeholder="e.g., Windows Server administrator")
    search_location = st.text_input("Job location", value="Egypt")
    job_col, course_col = st.columns(2)
    if job_col.button("Search live jobs", disabled=not bool(search_query.strip())):
        try:
            live = requests.get(f"{API_URL}/discover/jobs", params={"query": search_query, "where": search_location}, timeout=25)
            live.raise_for_status()
            payload = live.json()
            if not payload.get("configured"):
                st.info(payload.get("message", "Live job search is not configured."))
            elif not payload.get("items"):
                st.info("No live job results were returned for this query.")
            else:
                st.caption(f"Source: {payload.get('source')} · Results shown: {len(payload['items'])}")
                for item in payload["items"]:
                    st.markdown(f"**[{item['title']}]({item['url']})** — {item.get('company', 'Not specified')}")
                    st.caption(f"{item.get('location', '')} · {item.get('created') or ''}")
                    if item.get("description"):
                        st.write(item["description"])
        except Exception as exc:
            st.error(f"Live job search failed: {exc}")
    if course_col.button("Search live courses", disabled=not bool(search_query.strip())):
        try:
            live = requests.get(f"{API_URL}/discover/courses", params={"query": search_query}, timeout=25)
            live.raise_for_status()
            payload = live.json()
            if not payload.get("configured"):
                st.info(payload.get("message", "Live course search is not configured."))
            elif not payload.get("items"):
                st.info("No live course results were returned for this query.")
            else:
                st.caption(f"Source: {payload.get('source')} · Results shown: {len(payload['items'])}")
                for item in payload["items"]:
                    st.markdown(f"**[{item['title']}]({item['url']})** — {item.get('provider', 'Not specified')}")
                    if item.get("description"):
                        st.write(item["description"])
        except Exception as exc:
            st.error(f"Live course search failed: {exc}")

report = st.session_state.get("report")
if report:
    st.divider()

    # Automatically discover jobs and learning resources once per analysis.
    discovery_key = report.get("request_id")
    if discovery_key and st.session_state.get("auto_discovery_key") != discovery_key:
        gaps_to_learn = sorted(
            [
                gap for gap in report.get("gaps", [])
                if gap.get("status") in ("missing", "partial")
            ],
            key=lambda gap: gap.get("priority", 0),
            reverse=True,
        )[:3]

        course_query = " ".join(
            gap.get("skill_name", "") for gap in gaps_to_learn
        ).strip()

        st.session_state["auto_jobs"] = {
            "items": [], "message": "", "source": ""
        }
        st.session_state["auto_courses"] = {
            "items": [], "message": "", "source": ""
        }

        try:
            job_response = requests.get(
                f"{API_URL}/discover/jobs",
                params={"query": report.get("role_title", ""), "where": "Egypt", "limit": 5},
                timeout=25,
            )
            job_response.raise_for_status()
            st.session_state["auto_jobs"] = job_response.json()
        except Exception as exc:
            st.session_state["auto_jobs"] = {
                "items": [], "message": f"Job discovery unavailable: {type(exc).__name__}"
            }

        if course_query:
            try:
                course_response = requests.get(
                    f"{API_URL}/discover/courses",
                    params={"query": course_query, "limit": 5},
                    timeout=25,
                )
                course_response.raise_for_status()
                st.session_state["auto_courses"] = course_response.json()
            except Exception as exc:
                st.session_state["auto_courses"] = {
                    "items": [], "message": f"Course discovery unavailable: {type(exc).__name__}"
                }
        else:
            st.session_state["auto_courses"] = {
                "items": [], "message": "No missing or partial skills were identified for course search."
            }

        st.session_state["auto_discovery_key"] = discovery_key

    st.subheader("Live recommendations")
    st.caption("Jobs are searched using the target role. Learning resources are searched using the highest-priority missing or partial skills.")

    jobs_data = st.session_state.get("auto_jobs", {})
    courses_data = st.session_state.get("auto_courses", {})
    jobs_col, courses_col = st.columns(2)

    with jobs_col:
        st.markdown("#### Relevant jobs")
        if not jobs_data.get("configured", True):
            st.info(jobs_data.get("message", "Live job search is not configured."))
        elif jobs_data.get("message") and not jobs_data.get("items"):
            st.info(jobs_data["message"])
        elif not jobs_data.get("items"):
            st.info("No matching live jobs were found.")
        else:
            st.caption(f"Source: {jobs_data.get('source', 'Live job search')}")
            for job in jobs_data["items"]:
                title = job.get("title", "Untitled role")
                url = job.get("url", "")
                if url:
                    st.markdown(f"**[{title}]({url})**")
                else:
                    st.markdown(f"**{title}**")
                st.caption(
                    f"{job.get('company', 'Not specified')} · "
                    f"{job.get('location', '')}"
                )
                if job.get("description"):
                    st.write(job["description"])

    with courses_col:
        st.markdown("#### Learning resources for skill gaps")
        if not courses_data.get("configured", True):
            st.info(courses_data.get("message", "Live course search is not configured."))
        elif courses_data.get("message") and not courses_data.get("items"):
            st.info(courses_data["message"])
        elif not courses_data.get("items"):
            st.info("No matching learning resources were found.")
        else:
            st.caption(f"Source: {courses_data.get('source', 'Live course search')}")

            for course in courses_data["items"]:
                title = course.get("title", "Untitled learning resource")
                url = course.get("url", "")
                provider = course.get("provider", "Learning resource")
                description = course.get("description", "")
                matched_skill = course.get("matched_skill", "")

                title_lower = title.lower()
                url_lower = url.lower()
                text_to_check = f"{title_lower} {url_lower}"

                if any(word in text_to_check for word in (
                    "course", "training", "learning path", "academy",
                    "fundamentals", "certification"
                )):
                    resource_type = "Course / Training"
                elif any(word in text_to_check for word in (
                    "documentation", "docs.", "getting_started",
                    "get_started", "tutorial"
                )):
                    resource_type = "Documentation / Tutorial"
                elif any(word in text_to_check for word in (
                    "/blog/", "blog.", "/community/", "/question"
                )):
                    resource_type = "Article / Community"
                else:
                    resource_type = "Learning resource"

                st.markdown(f"**[{title}]({url})**" if url else f"**{title}**")
                st.caption(f"{provider} · {resource_type}")

                if matched_skill:
                    st.caption(f"Skill gap: {matched_skill}")

                if description:
                    st.write(description)


        # --- Summary ---
    c1, c2, c3 = st.columns(3)
    c1.metric(t("role"), report["role_title"])
    c2.metric(t("match_score"), f'{report["match_score"]:.0f}%')
    c3.metric(t("detected_skills"), len(report["candidate_profile"]["skills"]))
    st.progress(min(1.0, max(0.0, report["match_score"] / 100)))

    all_warnings = report.get("warnings", [])
    method_notes = [w for w in all_warnings if w.startswith("Skill extraction method")]
    for warning in all_warnings:
        if warning not in method_notes:
            st.warning(warning)

    # --- Skill gaps ---
    st.subheader(t("skill_gaps_title"))
    gaps = report["gaps"]
    skill_names = {g["skill_id"]: g["skill_name"] for g in gaps}

    def importance(weight):
        if weight >= 0.75:
            return t("importance_core")
        if weight >= 0.45:
            return t("importance_important")
        return t("importance_nice")

    status_groups = [
        ("missing", "❌", t("status_missing")),
        ("partial", "🟡", t("status_partial")),
        ("matched", "✅", t("status_matched")),
    ]
    for status, icon, label in status_groups:
        subset = sorted(
            [g for g in gaps if g["status"] == status],
            key=lambda g: g["weight"],
            reverse=True,
        )
        with st.expander(f"{icon} {label} ({len(subset)})", expanded=(status != "matched")):
            if not subset:
                st.write(t("none"))
            for gap in subset:
                st.markdown(f"**{gap['skill_name']}** · {importance(gap['weight'])}")
                if gap.get("evidence"):
                    st.caption(t("evidence") + " " + " | ".join(gap["evidence"]))

    # --- Recommendations ---
    st.subheader(t("recommendations_title"))
    if not report["recommendations"]:
        st.info(t("no_recommendations"))
    for item in report["recommendations"]:
        related = [skill_names[s] for s in item.get("skill_ids", []) if s in skill_names]
        st.markdown(
            f"**[{item['title']}]({item['url']})** — "
            f"{item['provider']} · {t('type_' + item['item_type'])}"
        )
        if related:
            st.caption(t("helps_with", skills=", ".join(related)))
        st.caption(t(
            "duration_level",
            duration=item.get("duration") or t("not_specified"),
            level=item.get("level") or t("all_levels"),
        ))

    # --- Roadmap ---
    st.subheader(t("roadmap_title"))
    if report["roadmap"]:
        for item in report["roadmap"]:
            phase = item["phase"].replace("Week", t("week"))
            st.markdown(f"**{phase} · {item['skill_name']}**")
            st.write(item["recommendation"]["title"])
    else:
        st.write(t("no_roadmap"))

    # --- Technical details (for developers) ---
    with st.expander(t("technical_details")):
        for note in method_notes:
            st.caption(note)
        st.download_button(
            t("download_json"),
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name="gap_report.json",
            mime="application/json",
        )

# RAG KNOWLEDGE ASSISTANT - UNIFIED DASHBOARD
st.divider()
st.header("AI Knowledge Assistant")
st.caption("Ask questions about your learning needs and indexed knowledge-base documents.")

current_report = st.session_state.get("report")

if current_report:
    current_gaps = sorted(
        [
            gap for gap in current_report.get("gaps", [])
            if gap.get("status") in ("missing", "partial")
        ],
        key=lambda gap: gap.get("priority", 0),
        reverse=True,
    )
    st.caption(f"Context: Target role — {current_report.get('role_title', 'Not specified')}")
    if current_gaps:
        st.write("Your current skill gaps:", ", ".join(
            gap.get("skill_name", "") for gap in current_gaps[:10]
        ))
    else:
        st.write("No missing or partial skills were identified in the current report.")

with st.form("unified_rag_question_form"):
    rag_question = st.text_area(
        "Your question",
        placeholder="For example: What should I learn first to improve my skills for this role?",
        max_chars=4000,
        key="unified_rag_question",
    )
    rag_top_k = st.slider(
        "Number of knowledge sources to retrieve",
        min_value=1,
        max_value=10,
        value=4,
        key="unified_rag_top_k",
    )
    rag_submitted = st.form_submit_button("Ask Knowledge Assistant", type="primary")

if rag_submitted:
    if not rag_question.strip():
        st.warning("Please enter a question.")
    else:
        user_question = rag_question.strip()
        context_parts = []

        if current_report:
            context_parts.append(
                f"Candidate target role: {current_report.get('role_title', 'Not specified')}."
            )
            context_parts.append(
                f"Candidate match score: {current_report.get('match_score', 'Not available')}%."
            )

            profile = current_report.get("candidate_profile") or {}
            detected_skills = profile.get("skills") or []
            if detected_skills:
                skill_names = []
                for skill in detected_skills[:15]:
                    if isinstance(skill, dict):
                        name = skill.get("skill_name") or skill.get("name")
                        if name:
                            skill_names.append(str(name))
                    elif isinstance(skill, str):
                        skill_names.append(skill)
                if skill_names:
                    context_parts.append(
                        "Skills detected in the candidate report (not independently verified): "
                        + ", ".join(skill_names) + "."
                    )

            if current_gaps:
                gap_details = [
                    f"{gap.get('skill_name', 'Unknown skill')} "
                    f"(status: {gap.get('status', 'unknown')}, "
                    f"weight: {gap.get('weight', 0)}, "
                    f"priority: {gap.get('priority', 0)})"
                    for gap in current_gaps[:10]
                ]
                context_parts.append(
                    "Candidate skill gaps from the report: "
                    + "; ".join(gap_details) + "."
                )

            recommendations = current_report.get("recommendations") or []
            if recommendations:
                rec_details = []
                for item in recommendations[:6]:
                    rec_details.append(
                        f"{item.get('title', 'Untitled')} "
                        f"({item.get('provider', 'Provider not specified')}; "
                        f"type: {item.get('item_type', 'unspecified')}; "
                        f"related skill: {item.get('reason', 'not specified')}; "
                        f"URL: {item.get('url', 'not provided')})"
                    )
                context_parts.append(
                    "Curated catalog recommendations from the report: "
                    + "; ".join(rec_details) + "."
                )

            roadmap = current_report.get("roadmap") or []
            if roadmap:
                roadmap_details = []
                for item in roadmap[:5]:
                    recommendation = item.get("recommendation") or {}
                    roadmap_details.append(
                        f"{item.get('phase', 'Phase not specified')}: "
                        f"{item.get('skill_name', 'Skill not specified')} ? "
                        f"{recommendation.get('title', 'No resource title')}"
                    )
                context_parts.append(
                    "Suggested roadmap from the report: "
                    + "; ".join(roadmap_details) + "."
                )

        prefix = (
            "Use the candidate report below to personalize the response. "
            "Treat report details as candidate-provided analysis, not knowledge-base "
            "evidence. Do not attribute skills from retrieved documents to this candidate. "
            "Use recommendations only when relevant, distinguish facts from suggestions, "
            "and cite only retrieved source IDs.\n\n"
        )
        context_text = "\n".join(context_parts)
        max_context_chars = 6000 - len(prefix)
        if len(context_text) > max_context_chars:
            context_text = context_text[:max_context_chars]

        with st.spinner("Searching the knowledge base and preparing an answer..."):
            try:
                rag_response = requests.post(
                    f"{API_URL}/rag/ask",
                    json={
                        "question": user_question,
                        "context": (prefix + context_text) if context_text else "",
                        "top_k": rag_top_k,
                    },
                    timeout=60,
                )
                rag_response.raise_for_status()
                rag_result = rag_response.json()
                st.session_state["unified_rag_result"] = rag_result
                st.session_state["unified_rag_error"] = None
            except requests.RequestException as exc:
                st.session_state["unified_rag_result"] = None
                st.session_state["unified_rag_error"] = str(exc)

if st.session_state.get("unified_rag_error"):
    st.error("The knowledge assistant request failed.")
    st.caption(st.session_state["unified_rag_error"])

rag_result = st.session_state.get("unified_rag_result")
if rag_result:
    st.subheader("Answer")
    st.write(rag_result.get("answer", "No answer was returned."))
    st.caption(f"Answer status: {rag_result.get('llm_status', 'unknown')}")

    citations = rag_result.get("citations", [])
    if citations:
        with st.expander(f"Sources ({len(citations)})", expanded=True):
            for citation in citations:
                st.markdown(
                    f"**[{citation.get('id', 'Source')}]** "
                    f"{citation.get('source', 'Unknown source')}"
                )
                st.caption(
                    f"File type: {citation.get('file_type', 'Unknown')} · "
                    f"Chunk: {citation.get('chunk_index', 'Unknown')} · "
                    f"Similarity: {citation.get('similarity', 'Unknown')}"
                )
    else:
        st.info("No supporting document sources were retrieved.")
