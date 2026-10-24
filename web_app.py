
import json
from pathlib import Path
from html import escape

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse

from Read_cv import extract_cv_text
from skill_matcher import extract_skills, analyze_skill_gap


# ==================================================
# 1. إعدادات التطبيق
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
JOBS_FILE = BASE_DIR / "data" / "jobs.json"

MAX_FILE_SIZE = 5 * 1024 * 1024

with JOBS_FILE.open("r", encoding="utf-8") as file:
    jobs = json.load(file)

app = FastAPI(title="TalentLink")


# ==================================================
# 2. تصميم الواجهة
# ==================================================

def page(content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>TalentLink | رحلتك المهنية</title>

        <style>
            :root {{
                --primary: #087f78;
                --primary-dark: #06645f;
                --navy: #192b4b;
                --muted: #65748b;
                --background: #f4f7fb;
                --border: #e0e7ef;
                --white: #ffffff;
            }}

            * {{
                box-sizing: border-box;
            }}

            html {{
                scroll-behavior: smooth;
            }}

            body {{
                margin: 0;
                color: var(--navy);
                background: var(--background);
                font-family: Tahoma, Arial, sans-serif;
                line-height: 1.8;
            }}

            a {{
                text-decoration: none;
            }}

            button, input, select {{
                font: inherit;
            }}

            /* ========== Header ========== */

            .site-header {{
                background: var(--white);
                border-bottom: 1px solid var(--border);
            }}

            .header-inner {{
                max-width: 1240px;
                min-height: 76px;
                margin: auto;
                padding: 12px 30px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 28px;
            }}

            .brand {{
                display: inline-flex;
                align-items: center;
                gap: 9px;
                color: var(--primary);
                font-size: 25px;
                font-weight: 800;
                direction: ltr;
                white-space: nowrap;
            }}

            .brand-symbol {{
                font-size: 32px;
                line-height: 1;
            }}

            .navigation {{
                display: flex;
                align-items: center;
                gap: 28px;
                flex-wrap: wrap;
            }}

            .navigation a {{
                color: var(--navy);
                font-size: 15px;
                font-weight: 600;
                transition: color 0.2s ease;
            }}

            .navigation a:hover {{
                color: var(--primary);
            }}

            .language-button {{
                border: 1px solid #dce4ed;
                border-radius: 24px;
                background: white;
                color: var(--navy);
                padding: 6px 17px;
                cursor: pointer;
                white-space: nowrap;
                transition: all 0.2s ease;
            }}

            .language-button:hover {{
                color: var(--primary);
                border-color: var(--primary);
            }}

            /* ========== Main ========== */

            .page-container {{
                max-width: 1180px;
                margin: auto;
                padding: 36px 28px 60px;
            }}

            /* ========== Progress ========== */

            .progress {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 18px;
                margin-bottom: 44px;
            }}

            .progress-step {{
                padding-top: 12px;
                border-top: 4px solid #dce3ed;
                color: var(--muted);
                font-size: 14px;
                font-weight: 600;
            }}

            .progress-step.active {{
                color: var(--navy);
                border-color: var(--primary);
            }}

            .step-number {{
                display: inline-flex;
                width: 27px;
                height: 27px;
                align-items: center;
                justify-content: center;
                margin-inline-end: 7px;
                border-radius: 50%;
                background: #e8edf4;
            }}

            .active .step-number {{
                background: var(--primary);
                color: white;
            }}

            /* ========== Hero ========== */

            .hero {{
                display: grid;
                grid-template-columns: minmax(0, 1.55fr)
                                       minmax(260px, 0.8fr);
                gap: 30px;
                align-items: stretch;
            }}

            .hero-main {{
                min-width: 0;
            }}

            .eyebrow {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 13px;
                border: 1px solid #cde9e5;
                border-radius: 30px;
                background: #eaf7f5;
                color: var(--primary-dark);
                font-size: 13px;
                font-weight: 700;
            }}

            .eyebrow-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--primary);
            }}

            h1 {{
                margin: 20px 0 12px;
                font-size: clamp(30px, 4vw, 43px);
                line-height: 1.4;
                letter-spacing: -0.5px;
            }}

            .hero-description {{
                max-width: 680px;
                margin: 0 0 27px;
                color: var(--muted);
                font-size: 17px;
                line-height: 1.9;
            }}

            /* ========== Upload Card ========== */

            .upload-card {{
                padding: 28px;
                border: 1px solid var(--border);
                border-radius: 18px;
                background: white;
                box-shadow: 0 10px 35px rgba(25, 43, 75, 0.045);
            }}

            .upload-zone {{
                padding: 28px 20px;
                border: 2px dashed #cbd9e8;
                border-radius: 13px;
                background: #fbfdff;
                text-align: center;
                transition: border-color 0.2s ease,
                            background 0.2s ease;
            }}

            .upload-zone:hover {{
                border-color: var(--primary);
                background: #f5fbfa;
            }}

            .file-icon {{
                display: flex;
                width: 62px;
                height: 62px;
                margin: 0 auto 12px;
                align-items: center;
                justify-content: center;
                border-radius: 16px;
                background: #e7f5f2;
                color: var(--primary);
                font-size: 30px;
            }}

            .upload-title {{
                margin: 0 0 5px;
                font-size: 18px;
                font-weight: 700;
            }}

            .upload-hint {{
                margin: 0 0 16px;
                color: var(--muted);
                font-size: 13px;
            }}

            .file-input {{
                display: block;
                width: 100%;
                max-width: 100%;
                padding: 10px;
                border: 1px solid var(--border);
                border-radius: 9px;
                background: white;
                color: var(--navy);
                font-size: 14px;
            }}

            .file-name {{
                min-height: 25px;
                margin-top: 10px;
                color: var(--primary-dark);
                font-size: 13px;
                overflow-wrap: anywhere;
            }}

            .field-label {{
                display: block;
                margin: 23px 0 8px;
                font-size: 14px;
                font-weight: 700;
            }}

            .job-select {{
                width: 100%;
                min-height: 48px;
                padding: 10px 13px;
                border: 1px solid #d7e0eb;
                border-radius: 9px;
                background: white;
                color: var(--navy);
            }}

            .primary-button {{
                display: flex;
                width: 100%;
                min-height: 50px;
                align-items: center;
                justify-content: center;
                gap: 10px;
                margin-top: 22px;
                padding: 12px 20px;
                border: none;
                border-radius: 9px;
                background: var(--primary);
                color: white;
                font-weight: 700;
                cursor: pointer;
                transition: background 0.2s ease,
                            transform 0.2s ease;
            }}

            .primary-button:hover {{
                background: var(--primary-dark);
                transform: translateY(-1px);
            }}

            .primary-button:focus-visible {{
                outline: 3px solid #a5ded7;
                outline-offset: 3px;
            }}

            .file-rules {{
                display: grid;
                gap: 8px;
                margin: 20px 0 0;
                padding: 0;
                list-style: none;
                color: var(--muted);
                font-size: 13px;
            }}

            .file-rules li {{
                display: flex;
                align-items: flex-start;
                gap: 9px;
            }}

            .rule-check {{
                color: var(--primary);
                font-weight: 800;
            }}

            /* ========== Side Information Card ========== */

            .side-card {{
                align-self: stretch;
                padding: 27px;
                border: 1px solid #dcebe9;
                border-radius: 18px;
                background: linear-gradient(
                    155deg, #e8f6f3 0%, #f9fcff 75%
                );
            }}

            .side-illustration {{
                display: flex;
                width: 76px;
                height: 76px;
                align-items: center;
                justify-content: center;
                margin-bottom: 23px;
                border: 1px solid #d4e9e5;
                border-radius: 20px;
                background: white;
                color: var(--primary);
                font-size: 37px;
            }}

            .side-card h2 {{
                margin: 0 0 10px;
                font-size: 22px;
                line-height: 1.6;
            }}

            .side-card > p {{
                margin: 0;
                color: var(--muted);
                font-size: 14px;
            }}

            .benefits {{
                display: grid;
                gap: 18px;
                margin-top: 26px;
            }}

            .benefit {{
                display: flex;
                align-items: flex-start;
                gap: 12px;
            }}

            .benefit-icon {{
                display: flex;
                flex-shrink: 0;
                width: 35px;
                height: 35px;
                align-items: center;
                justify-content: center;
                border-radius: 10px;
                background: white;
                color: var(--primary);
                font-size: 17px;
                font-weight: 700;
            }}

            .benefit strong {{
                display: block;
                margin-bottom: 2px;
                font-size: 14px;
            }}

            .benefit span {{
                display: block;
                color: var(--muted);
                font-size: 12px;
                line-height: 1.7;
            }}

            .privacy-note {{
                margin-top: 22px;
                padding: 13px 15px;
                border: 1px solid #dcebe9;
                border-radius: 10px;
                background: rgba(255,255,255,0.8);
                color: #526580;
                font-size: 12px;
                line-height: 1.9;
            }}

            /* ========== Results ========== */

            .result-card {{
                margin-top: 28px;
                padding: 28px;
                border: 1px solid var(--border);
                border-radius: 16px;
                background: white;
            }}

            .result-box {{
                margin: 15px 0;
                padding: 17px;
                border-radius: 10px;
                background: #eaf6f3;
            }}

            .skills-list li {{
                margin-bottom: 7px;
            }}

            .error {{
                margin-top: 20px;
                padding: 18px;
                border-radius: 10px;
                background: #fff0ef;
                color: #a52620;
            }}

            .back-link {{
                display: inline-block;
                margin-top: 20px;
                color: var(--primary-dark);
                font-weight: 700;
            }}

            /* ========== Footer ========== */

            .site-footer {{
                border-top: 1px solid var(--border);
                background: white;
            }}

            .footer-inner {{
                max-width: 1180px;
                margin: auto;
                padding: 24px 28px 30px;
            }}

            .footer-description {{
                max-width: 850px;
                margin: 0 0 12px;
                color: var(--muted);
                font-size: 13px;
                line-height: 1.9;
            }}

            .footer-links {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px 22px;
            }}

            .footer-links a {{
                color: var(--primary-dark);
                font-size: 13px;
                text-decoration: underline;
                text-underline-offset: 3px;
                transition: color 0.2s ease;
            }}

            .footer-links a:first-child {{
                color: #b42335;
            }}

            .footer-links a:hover {{
                color: var(--navy);
            }}

            /* ========== Responsive ========== */

            @media (max-width: 850px) {{
                .header-inner {{
                    flex-wrap: wrap;
                    gap: 16px;
                }}

                .navigation {{
                    gap: 14px 20px;
                }}

                .hero {{
                    grid-template-columns: 1fr;
                }}

                .side-card {{
                    display: grid;
                    grid-template-columns: 70px 1fr;
                    column-gap: 18px;
                }}

                .side-illustration {{
                    grid-row: span 2;
                    width: 65px;
                    height: 65px;
                }}

                .benefits, .privacy-note {{
                    grid-column: 1 / -1;
                }}
            }}

            @media (max-width: 540px) {{
                .header-inner {{
                    padding: 15px 18px;
                }}

                .navigation {{
                    width: 100%;
                    gap: 12px 16px;
                }}

                .navigation a {{
                    font-size: 13px;
                }}

                .page-container {{
                    padding: 24px 16px 40px;
                }}

                .progress {{
                    gap: 8px;
                    margin-bottom: 28px;
                }}

                .progress-step {{
                    font-size: 11px;
                }}

                .step-number {{
                    width: 23px;
                    height: 23px;
                    margin-inline-end: 3px;
                }}

                h1 {{
                    font-size: 30px;
                }}

                .hero-description {{
                    font-size: 15px;
                }}

                .upload-card, .side-card {{
                    padding: 20px;
                }}

                .footer-inner {{
                    padding: 20px 18px 26px;
                }}
            }}
        </style>
    </head>

    <body>

        <header class="site-header">
            <div class="header-inner">

                <a class="brand" href="/">
                    <span>TalentLink</span>
                    <span class="brand-symbol">∿</span>
                </a>

                <nav class="navigation" aria-label="Main navigation">

                    <button
                        id="language-button"
                        class="language-button"
                        type="button"
                        onclick="toggleLanguage()">
                        English
                    </button>

                    <a href="#companies"
                       data-ar="للشركات"
                       data-en="For Companies">
                        للشركات
                    </a>

                    <a href="#jobs"
                       data-ar="الوظائف"
                       data-en="Jobs">
                        الوظائف
                    </a>

                    <a href="#plans"
                       data-ar="خططي"
                       data-en="My Plans">
                        خططي
                    </a>

                    <a href="/"
                       data-ar="خطة جديدة"
                       data-en="New Plan">
                        خطة جديدة
                    </a>

                </nav>
            </div>
        </header>

        <main class="page-container">

            <div class="progress">

                <div class="progress-step active">
                    <span class="step-number">1</span>
                    <span data-ar="سيرتك الذاتية"
                          data-en="Your CV">
                        سيرتك الذاتية
                    </span>
                </div>

                <div class="progress-step">
                    <span class="step-number">2</span>
                    <span data-ar="هدفك المهني"
                          data-en="Your Goal">
                        هدفك المهني
                    </span>
                </div>

                <div class="progress-step">
                    <span class="step-number">3</span>
                    <span data-ar="خطة التطوير"
                          data-en="Your Plan">
                        خطة التطوير
                    </span>
                </div>

            </div>

            {content}

        </main>

        <footer class="site-footer">
            <div class="footer-inner">

                <p class="footer-description"
                   data-ar="خصوصيتك مهمة. في هذه النسخة الأولية، تتم معالجة الملف داخل التطبيق دون حفظه في ملف دائم. ستُنفّذ إدارة البيانات المحفوظة والحذف عند إضافة هذه الوظائف."
                   data-en="Your privacy matters. In this initial version, the file is processed by the application without being saved as a persistent file. Saved-data management and deletion will be implemented when those features are added.">
                    خصوصيتك مهمة. في هذه النسخة الأولية، تتم معالجة الملف
                    داخل التطبيق دون حفظه في ملف دائم. ستُنفّذ إدارة
                    البيانات المحفوظة والحذف عند إضافة هذه الوظائف.
                </p>

                <div class="footer-links">
                    <a href="/delete-my-data"
                       data-ar="حذف بياناتي"
                       data-en="Delete my data">
                        حذف بياناتي
                    </a>

                    <a href="/privacy"
                       data-ar="الخصوصية والبيانات"
                       data-en="Privacy and your data">
                        الخصوصية والبيانات
                    </a>
                </div>

            </div>
        </footer>

        <script>
            let currentLanguage = "ar";

            function toggleLanguage() {{
                currentLanguage =
                    currentLanguage === "ar" ? "en" : "ar";

                document.documentElement.lang = currentLanguage;
                document.documentElement.dir =
                    currentLanguage === "ar" ? "rtl" : "ltr";

                document.querySelectorAll("[data-ar][data-en]")
                    .forEach(function(element) {{
                        element.textContent =
                            element.getAttribute(
                                "data-" + currentLanguage
                            );
                    }});

                document.getElementById("language-button")
                    .textContent =
                        currentLanguage === "ar"
                            ? "English"
                            : "العربية";
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                const fileInput = document.getElementById("file");
                const fileName = document.getElementById("file-name");

                if (fileInput && fileName) {{
                    fileInput.addEventListener("change", function() {{
                        const file = fileInput.files[0];

                        if (!file) {{
                            fileName.textContent = "";
                            return;
                        }}

                        fileName.textContent = file.name;
                    }});
                }}
            }});
        </script>

    </body>
    </html>
    """


# ==================================================
# 3. الصفحة الرئيسية
# ==================================================

@app.get("/", response_class=HTMLResponse)
async def home():

    options = "".join(
        f'<option value="{i}">{escape(str(job["title"]))}</option>'
        for i, job in enumerate(jobs)
    )

    content = f"""
    <section class="hero">

        <div class="hero-main">

            <div class="eyebrow">
                <span class="eyebrow-dot"></span>
                <span
                    data-ar="خطوتك الأولى نحو فرصتك القادمة"
                    data-en="Your first step toward your next opportunity">
                    خطوتك الأولى نحو فرصتك القادمة
                </span>
            </div>

            <h1
                data-ar="ابدأ رحلتك المهنية بخطوة ذكية"
                data-en="Take a smarter step in your career">
                ابدأ رحلتك المهنية بخطوة ذكية
            </h1>

            <p class="hero-description"
               data-ar="اكتشف المهارات التي تمتلكها، وقارنها بمتطلبات الوظيفة التي تختارها، وحدد خطواتك التالية نحو تطوير مسارك المهني."
               data-en="Discover your skills, compare them with your chosen job requirements, and identify the next steps in your career development.">
                اكتشف المهارات التي تمتلكها، وقارنها بمتطلبات الوظيفة
                التي تختارها، وحدد خطواتك التالية نحو تطوير مسارك المهني.
            </p>

            <div class="upload-card">

                <form action="/analyze"
                      method="post"
                      enctype="multipart/form-data">

                    <div class="upload-zone">

                        <div class="file-icon">↥</div>

                        <p class="upload-title"
                           data-ar="ارفع سيرتك الذاتية"
                           data-en="Upload your CV">
                            ارفع سيرتك الذاتية
                        </p>

                        <p class="upload-hint"
                           data-ar="اختر ملفك من جهازك بصيغة PDF أو DOCX"
                           data-en="Choose a PDF or DOCX file from your device">
                            اختر ملفك من جهازك بصيغة PDF أو DOCX
                        </p>

                        <input
                            class="file-input"
                            id="file"
                            type="file"
                            name="file"
                            accept=".pdf,.docx"
                            required>

                        <div class="file-name"
                             id="file-name"
                             aria-live="polite">
                        </div>

                    </div>

                    <label class="field-label"
                           for="job_index"
                           data-ar="ما الوظيفة التي تستهدفها؟"
                           data-en="Which job are you targeting?">
                        ما الوظيفة التي تستهدفها؟
                    </label>

                    <select
                        class="job-select"
                        id="job_index"
                        name="job_index"
                        required>
                        {options}
                    </select>

                    <ul class="file-rules">

                        <li>
                            <span class="rule-check">✓</span>
                            <span
                                data-ar="الصيغ المدعومة: PDF وWord بصيغة DOCX."
                                data-en="Supported formats: PDF and Word (DOCX).">
                                الصيغ المدعومة: PDF وWord بصيغة DOCX.
                            </span>
                        </li>

                        <li>
                            <span class="rule-check">✓</span>
                            <span
                                data-ar="الحد الأقصى لحجم الملف 5 ميجابايت."
                                data-en="Maximum file size: 5 MB.">
                                الحد الأقصى لحجم الملف 5 ميجابايت.
                            </span>
                        </li>

                        <li>
                            <span class="rule-check">✓</span>
                            <span
                                data-ar="يجب أن يحتوي الملف على نص قابل للاستخراج."
                                data-en="The file must contain extractable text.">
                                يجب أن يحتوي الملف على نص قابل للاستخراج.
                            </span>
                        </li>

                    </ul>

                    <button
                        class="primary-button"
                        type="submit">
                        <span
                            data-ar="تحليل السيرة الذاتية"
                            data-en="Analyze my CV">
                            تحليل السيرة الذاتية
                        </span>
                        <span aria-hidden="true">←</span>
                    </button>

                </form>

            </div>

        </div>


        <aside class="side-card">

            <div class="side-illustration">✦</div>

            <h2
                data-ar="مسارك المهني يبدأ من هنا"
                data-en="Your career journey starts here">
                مسارك المهني يبدأ من هنا
            </h2>

            <p
                data-ar="خطوات واضحة تساعدك على فهم وضعك الحالي والاستعداد للفرصة التي تستهدفها."
                data-en="Clear steps to understand where you stand and prepare for the opportunity you want.">
                خطوات واضحة تساعدك على فهم وضعك الحالي والاستعداد
                للفرصة التي تستهدفها.
            </p>

            <div class="benefits">

                <div class="benefit">
                    <div class="benefit-icon">✓</div>
                    <div>
                        <strong
                            data-ar="اكتشف مهاراتك"
                            data-en="Discover your skills">
                            اكتشف مهاراتك
                        </strong>
                        <span
                            data-ar="استخرج المهارات والخبرات المذكورة في سيرتك الذاتية."
                            data-en="Identify skills and experience mentioned in your CV.">
                            استخرج المهارات والخبرات المذكورة في سيرتك الذاتية.
                        </span>
                    </div>
                </div>

                <div class="benefit">
                    <div class="benefit-icon">◎</div>
                    <div>
                        <strong
                            data-ar="قارن بمتطلبات الوظيفة"
                            data-en="Compare job requirements">
                            قارن بمتطلبات الوظيفة
                        </strong>
                        <span
                            data-ar="تعرف على المهارات المتوافقة والمهارات التي لم تظهر في سيرتك."
                            data-en="See matching skills and those not found in your CV.">
                            تعرف على المهارات المتوافقة والمهارات
                            التي لم تظهر في سيرتك.
                        </span>
                    </div>
                </div>

                <div class="benefit">
                    <div class="benefit-icon">↗</div>
                    <div>
                        <strong
                            data-ar="خطط لخطوتك التالية"
                            data-en="Plan your next step">
                            خطط لخطوتك التالية
                        </strong>
                        <span
                            data-ar="استعد لاحقًا لخطة تطوير مبنية على احتياجاتك."
                            data-en="Prepare for a learning plan based on your needs.">
                            استعد لاحقًا لخطة تطوير مبنية على احتياجاتك.
                        </span>
                    </div>
                </div>

            </div>

            <div class="privacy-note"
                 data-ar="الخصوصية أولًا: لا ترسل سيرتك الذاتية إلى أي نموذج ذكاء اصطناعي قبل إضافة خطوة تنقيح البيانات الشخصية."
                 data-en="Privacy first: your CV will not be sent to an AI model before a personal-data redaction step is implemented.">
                الخصوصية أولًا: لا ترسل سيرتك الذاتية إلى أي نموذج
                ذكاء اصطناعي قبل إضافة خطوة تنقيح البيانات الشخصية.
            </div>

        </aside>

    </section>
    """

    return page(content)


# ==================================================
# 4. قراءة الملف ومقارنة المهارات
# ==================================================

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    file: UploadFile = File(...),
    job_index: int = Form(...),
):

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        return HTMLResponse(
            page("""
                <div class="error">
                    <h2
                        data-ar="نوع الملف غير مدعوم"
                        data-en="Unsupported file type">
                        نوع الملف غير مدعوم
                    </h2>
                    <p
                        data-ar="يرجى اختيار ملف PDF أو DOCX."
                        data-en="Please choose a PDF or DOCX file.">
                        يرجى اختيار ملف PDF أو DOCX.
                    </p>
                    <a class="back-link" href="/">العودة</a>
                </div>
            """),
            status_code=400,
        )

    if not 0 <= job_index < len(jobs):
        return HTMLResponse(
            page("""
                <div class="error">
                    اختيار الوظيفة غير صالح.
                    <a class="back-link" href="/">العودة</a>
                </div>
            """),
            status_code=400,
        )

    try:
        content = await file.read(MAX_FILE_SIZE + 1)
    finally:
        await file.close()

    if len(content) > MAX_FILE_SIZE:
        return HTMLResponse(
            page("""
                <div class="error">
                    حجم الملف يتجاوز الحد المسموح به وهو 5 ميجابايت.
                    <a class="back-link" href="/">العودة</a>
                </div>
            """),
            status_code=413,
        )

    try:
        # يفترض أن extract_cv_text تستقبل اسم الملف ومحتواه.
        cv_text = extract_cv_text(filename, content)

    except Exception:
        return HTMLResponse(
            page("""
                <div class="error">
                    <h2>تعذرت قراءة الملف.</h2>
                    <p>
                        يرجى التأكد من سلامة الملف واحتوائه على نص قابل للاستخراج.
                    </p>
                    <a class="back-link" href="/">العودة</a>
                </div>
            """),
            status_code=400,
        )

    if not cv_text or not cv_text.strip():
        return HTMLResponse(
            page("""
                <div class="error">
                    لم يتم العثور على نص قابل للاستخراج من الملف.
                    قد يكون ملف PDF صورة ممسوحة ضوئيًا.
                    <a class="back-link" href="/">العودة</a>
                </div>
            """),
            status_code=400,
        )

    selected_job = jobs[job_index]
    required_skills = selected_job.get("required_skills", [])

    # البحث عن الكلمات المفتاحية المطلوبة داخل نص السيرة الذاتية.
    candidate_skills = extract_skills(cv_text, required_skills)

    # ملاحظة: هذه الواجهة تفترض أن الدالة تعيد قاموسًا
    # يحتوي على matched_skills وmissing_skills وmatch_rate.
    report = analyze_skill_gap(candidate_skills, required_skills)

    matched_html = "".join(
        f"<li>{escape(str(skill))}</li>"
        for skill in report["matched_skills"]
    ) or "<li>لم يتم العثور على مهارات متطابقة.</li>"

    missing_html = "".join(
        f"<li>{escape(str(skill))}</li>"
        for skill in report["missing_skills"]
    ) or "<li>لم يتم العثور على مهارات ناقصة.</li>"

    content = f"""
    <section class="result-card">

        <h1
            data-ar="نتيجة تحليل السيرة الذاتية"
            data-en="CV Analysis Results">
            نتيجة تحليل السيرة الذاتية
        </h1>

        <p class="muted">
            <strong
                data-ar="الوظيفة المستهدفة:"
                data-en="Target job:">
                الوظيفة المستهدفة:
            </strong>
            {escape(str(selected_job["title"]))}
        </p>

        <div class="result-box">
            <h2
                data-ar="نسبة تطابق الكلمات المفتاحية"
                data-en="Keyword Match Rate">
                نسبة تطابق الكلمات المفتاحية
            </h2>
            <h2>{report["match_rate"]:.1f}%</h2>
        </div>

        <h2
            data-ar="المهارات التي عُثر عليها"
            data-en="Matched Skills">
            المهارات التي عُثر عليها
        </h2>
        <ul class="skills-list">{matched_html}</ul>

        <h2
            data-ar="المهارات التي لم يُعثر عليها"
            data-en="Skills Not Found">
            المهارات التي لم يُعثر عليها
        </h2>
        <ul class="skills-list">{missing_html}</ul>

        <p class="muted"
           data-ar="هذه نتيجة أولية تعتمد على الكلمات المفتاحية، ولا تثبت مستوى إتقان المهارات. كما أن عدم العثور على كلمة لا يعني بالضرورة أن المرشح لا يمتلك المهارة."
           data-en="This preliminary result uses keyword matching and does not establish proficiency. A missing keyword does not necessarily mean the candidate lacks that skill.">
            هذه نتيجة أولية تعتمد على الكلمات المفتاحية، ولا تثبت
            مستوى إتقان المهارات. كما أن عدم العثور على كلمة لا يعني
            بالضرورة أن المرشح لا يمتلك المهارة.
        </p>

        <a class="back-link" href="/"
           data-ar="العودة لتحليل سيرة ذاتية أخرى"
           data-en="Analyze another CV">
            العودة لتحليل سيرة ذاتية أخرى
        </a>

    </section>
    """

    return page(content)
