from pathlib import Path

path = Path("frontend/app.py")
source = path.read_text(encoding="utf-8-sig")

marker = '''if report:
    st.divider()
    c1, c2, c3 = st.columns(3)
'''

replacement = '''if report:
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
                if url:
                    st.markdown(f"**[{title}]({url})**")
                else:
                    st.markdown(f"**{title}**")
                st.caption(course.get("provider", "Learning resource"))
                if course.get("description"):
                    st.write(course["description"])

    c1, c2, c3 = st.columns(3)
'''

if source.count(marker) != 1:
    raise SystemExit(
        "Expected frontend insertion point was not found exactly once. No changes made."
    )

updated = source.replace(marker, replacement, 1)
path.write_text(updated, encoding="utf-8")
print("Updated frontend/app.py with automatic live discovery.")
