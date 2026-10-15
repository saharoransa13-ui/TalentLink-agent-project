
import json
from pathlib import Path
from datetime import date
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup


# 1. الصفحة العامة التي سنجمع منها الدورات
CATALOG_URL = (
    "https://maharatech.gov.eg/course/"
    "index.php?categoryid=196&lang=en"
)

# 2. مكان حفظ البيانات
OUTPUT_PATH = Path("data/learning_resources.json")


# 3. جمع أسماء الدورات وروابطها من صفحة الكتالوج
def collect_courses(catalog_url):
    response = requests.get(
        catalog_url,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    courses_by_url = {}

    for link in soup.find_all("a", href=True):
        href = link["href"]

        # نهتم بروابط صفحات الدورات فقط
        if "/course/view.php" not in href:
            continue

        title = " ".join(
            link.get_text(" ", strip=True).split()
        )

        # تجاهل روابط المعاينة العامة
        if title.casefold() in {
            "preview course",
            "preview",
            "استعراض الدورة التدريبية"
        }:
            continue

        # لو الرابط لا يحتوي على نص، نحاول قراءة اسم الصورة
        if not title:
            image = link.find("img")
            if image:
                title = (image.get("alt") or "").strip()

        if not title:
            continue

        course_url = urljoin(catalog_url, href)

        # استخراج رقم الدورة من الرابط
        query_parameters = parse_qs(
            urlparse(course_url).query
        )

        course_id = query_parameters.get(
            "id", ["unknown"]
        )[0]

        courses_by_url[course_url] = {
            "resource_id": f"maharatech_{course_id}",
            "provider": "Mahara-Tech",
            "course_title": title,
            "source_url": course_url,
            "catalog_url": catalog_url
        }

    return list(courses_by_url.values())


# 4. حفظ الدورات الجديدة مع الاحتفاظ بالسجلات الموجودة
def save_courses(new_courses):
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_PATH.exists():
        with OUTPUT_PATH.open(
            "r", encoding="utf-8"
        ) as file:
            resources = json.load(file)
    else:
        resources = []

    if not isinstance(resources, list):
        raise ValueError(
            "learning_resources.json must contain a JSON list."
        )

    resources_by_url = {}

    for resource in resources:
        if resource.get("source_url"):
            resources_by_url[
                resource["source_url"]
            ] = resource

    added_count = 0
    updated_count = 0
    today = date.today().isoformat()

    for course in new_courses:
        course_url = course["source_url"]

        if course_url in resources_by_url:
            # تحديث معلومات الدورة دون حذف بياناتها الأخرى
            existing = resources_by_url[course_url]
            existing["course_title"] = course["course_title"]
            existing["catalog_url"] = course["catalog_url"]
            existing["last_seen"] = today

            updated_count += 1

        else:
            # تسجيل دورة جديدة
            resource = {
                **course,
                "topics": [],
                "credential_names": [],
                "collected_at": today,
                "last_seen": today,
                "review_status": "catalog_only"
            }

            resources.append(resource)
            resources_by_url[course_url] = resource

            added_count += 1

    with OUTPUT_PATH.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            resources,
            file,
            ensure_ascii=False,
            indent=4
        )

    return added_count, updated_count, len(resources)


# 5. تشغيل عملية الجمع والحفظ
def main():
    try:
        courses = collect_courses(CATALOG_URL)

        if not courses:
            print(
                "No courses found. "
                "The website structure may have changed."
            )
            return

        added, updated, total = save_courses(courses)

        print("Courses found:", len(courses))
        print("New courses added:", added)
        print("Existing courses refreshed:", updated)
        print("Total resources saved:", total)
        print("Output file:", OUTPUT_PATH)

        print("\nCollected courses:")

        for course in courses:
            print(
                "-",
                course["course_title"],
                "->",
                course["source_url"]
            )

    except requests.RequestException as error:
        print("Could not access the website:", error)

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("Could not process the data file:", error)


if __name__ == "__main__":
    main()
