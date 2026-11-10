import json
from pathlib import Path
from typing import List
from backend.schemas import Recommendation, RoadmapItem, SkillGap

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "catalog.json"

def load_catalog():
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def recommend(gaps: List[SkillGap]):
    catalog = load_catalog()
    valid_ids = {item["item_id"] for item in catalog}
    recs = []
    roadmap = []
    seen = set()
    phase_num = 1
    for gap in gaps:
        if gap.score >= 1:
            continue
        candidates = [
            item for item in catalog
            if gap.skill_id in item.get("skill_ids", [])
        ]
        for item in candidates[:2]:
            if item["item_id"] in seen or item["item_id"] not in valid_ids:
                continue
            seen.add(item["item_id"])
            reason = f"Targets the {gap.skill_name} gap (priority {gap.priority:.2f}) and is present in the curated catalog."
            rec = Recommendation(
                item_id=item["item_id"], title=item["title"], item_type=item["item_type"],
                provider=item["provider"], url=item["url"], skill_ids=item["skill_ids"],
                level=item.get("level", "all"), duration=item.get("duration", ""),
                reason=reason
            )
            recs.append(rec)
            phase = "Week 1–2" if phase_num <= 2 else ("Week 3–4" if phase_num <= 4 else "Week 5–6")
            roadmap.append(RoadmapItem(
                phase=phase, skill_id=gap.skill_id, skill_name=gap.skill_name,
                recommendation=rec, reason=reason
            ))
            phase_num += 1
            if phase_num > 6:
                break
        if phase_num > 6:
            break
    return recs, roadmap
