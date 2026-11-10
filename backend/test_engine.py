from backend.extractor import extract_candidate_profile
from backend.main import load_roles
from backend.skill_engine import calculate_gaps

def test_extractor_detects_networking_and_linux():
    profile = extract_candidate_profile("I have experience with TCP/IP, routing, switching and Linux.")
    ids = {s.skill_id for s in profile.skills}
    assert "networking" in ids
    assert "linux" in ids

def test_score_is_bounded_and_deterministic():
    profile = extract_candidate_profile("Python, machine learning, PyTorch, RAG and generative AI.")
    role = load_roles()["ai_ml"]
    score1, gaps1 = calculate_gaps(profile, role)
    score2, gaps2 = calculate_gaps(profile, role)
    assert 0 <= score1 <= 100
    assert score1 == score2
    assert [g.skill_id for g in gaps1] == [g.skill_id for g in gaps2]

def test_all_roles_have_skills():
    roles = load_roles()
    assert len(roles) >= 8
    assert all(role.skills for role in roles.values())



def test_sysadmin_gaps_have_catalog_recommendations():
    from backend.recommender import load_catalog, recommend
    from backend.schemas import SkillGap

    catalog_skill_ids = {
        skill_id
        for item in load_catalog()
        for skill_id in item.get("skill_ids", [])
    }
    assert "windows_server" in catalog_skill_ids
    assert "backup" in catalog_skill_ids

    gaps = [
        SkillGap(
            skill_id="windows_server",
            skill_name="Windows Server",
            weight=0.9,
            status="missing",
            score=0.0,
            priority=0.9,
            prerequisite=False,
            evidence=[]
        ),
        SkillGap(
            skill_id="backup",
            skill_name="Backup & Recovery",
            weight=0.7,
            status="missing",
            score=0.0,
            priority=0.7,
            prerequisite=False,
            evidence=[]
        ),
    ]
    recommendations, roadmap = recommend(gaps)
    recommended_skills = {
        skill_id for item in recommendations for skill_id in item.skill_ids
    }
    assert "windows_server" in recommended_skills
    assert "backup" in recommended_skills
    assert recommendations
    assert roadmap


def test_semantic_match_is_partial_not_full_credit():
    from backend.schemas import CandidateProfile, JobProfile, RoleSkill
    from backend.skill_engine import calculate_gaps

    candidate = CandidateProfile(skills=[])
    role = JobProfile(role_id="test", title="Test", skills=[
        RoleSkill(skill_id="windows_server", name="Windows Server", weight=1.0, aliases=["active directory"])
    ])
    score, gaps = calculate_gaps(candidate, role, semantic_matches={"windows_server": (0.76, "Managed enterprise directory services")})
    assert score == 50.0
    assert gaps[0].status == "partial"
    assert gaps[0].score == 0.5
    assert "Semantic evidence" in gaps[0].evidence[0]


def test_live_discovery_reports_missing_credentials(monkeypatch):
    from backend.live_sources import search_jobs, search_courses
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    jobs = search_jobs("systems administrator")
    courses = search_courses("windows server")
    assert jobs["configured"] is False and jobs["items"] == []
    assert courses["configured"] is False and courses["items"] == []


def test_smart_extractor_uses_rules_when_llm_not_configured(monkeypatch):
    from backend.llm_extractor import extract_candidate_profile_smart
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    profile, method, warning = extract_candidate_profile_smart("I work with Linux and TCP/IP.", "cv.txt")
    assert method == "rules"
    assert warning is None
    assert {s.skill_id for s in profile.skills} >= {"linux", "networking"}
