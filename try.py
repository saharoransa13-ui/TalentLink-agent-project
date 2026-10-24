from pathlib import Path
from Read_cv import extract_cv_text
from cv_llm import read_cv_with_llm          # new

path = Path(r"D:\talentlink\data\cvs\synthetic\da_cv_01.pdf")

cv_text = extract_cv_text(path.name, path.read_bytes())
print("Characters:", len(cv_text))

profile = read_cv_with_llm(cv_text)          # new
print(profile.model_dump_json(indent=2))     # new