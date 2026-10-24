import re

#cv_text = """
#Name: Sahar
#Email: sahar.oransa@example.com
#Experience: Python developer
#"""

#NAME=re.compile(text.splitlines())
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


PHONE = re.compile(
    r"(?<!\d)(?:\+20[\s-]?|0)1[0125](?:[\s-]?\d){8}(?!\d)"
)



LINK = re.compile(
    r"https?://\S+|www\.\S+|linkedin\.com/\S+|github\.com\S+"
)

NAME_LABEL = re.compile(r"^\s*(?:full\s+)?name\s*[:\-]\s*\S.*$", re.IGNORECASE | re.MULTILINE)


def redact_name(text: str) -> str:
    lines = text.splitlines()                 # 1. the text as a list of lines
    for i, line in enumerate(lines):          # 2. i = line number, line = its text
        stripped = line.strip()
        if not stripped:                      # 3. an empty line at the top: skip it
            continue
        words = stripped.split()              # 4. "Sara Ahmed Hassan" -> ["Sara", "Ahmed", "Hassan"]
        if 2 <= len(words) <= 4 and not any(
            ch.isdigit() for ch in stripped):                              
            lines[i] = "[NAME]"
        break                                 # 6. only the FIRST non-empty line is checked
    return "\n".join(lines)                   # 7. back to one text

def redact_pii(text: str) -> str:
     text = EMAIL.sub("[EMAIL]", text)
     text = PHONE.sub("[PHONE]", text)
     text= LINK.sub("[LINK]",text)
     text = NAME_LABEL.sub("Name: [NAME]", text)
     text = redact_name(text)

     return text  

#clean_text = redact_pii(cv_text)
#print(clean_text)