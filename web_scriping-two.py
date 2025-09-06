import os
import re
import sqlite3
import random
import time
import requests
from io import BytesIO
from PIL import Image

# ================= إعداد المسارات =================
IMG_DIR = r"C:\my\Projectes\Summer Proejct (SP)\Main Fill of SP\static\img"
BOOK_DIR = r"C:\my\Projectes\Summer Proejct (SP)\Main Fill of SP\static\Books"
DB_PATH = r"C:\my\Projectes\Summer Proejct (SP)\Main Fill of SP\library_DB.db"

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(BOOK_DIR, exist_ok=True)

# ================= دوال مساعدة =================

def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/*?:\"<>|]", "_", name).strip()
    name = re.sub(r"\s+", "_", name)
    return name[:120]


def http_get_json(url, params=None, timeout=20):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ GET JSON فشل: {url} -> {e}")
        return None


def fetch_description(work_key: str) -> str:
    """يجلب وصف العمل من /works/{key}.json إن توفر."""
    if not work_key:
        return ""
    url = f"https://openlibrary.org{work_key}.json"
    data = http_get_json(url)
    if not data:
        return ""
    desc = data.get("description")
    if isinstance(desc, dict):
        return desc.get("value", "").strip()
    if isinstance(desc, str):
        return desc.strip()
    return ""


def cover_url_from_id(cover_i):
    if not cover_i:
        return None
    return f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"


def save_image(url: str, title: str) -> str:
    if not url:
        return "default.jpg"
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        img = img.convert("RGB")
        fname = sanitize_filename(title) + ".jpg"
        path = os.path.join(IMG_DIR, fname)
        img.save(path, format="JPEG", quality=90)
        return f"/static/img/{fname}"
    except Exception as e:
        print(f"⚠️ حفظ الصورة فشل: {e}")
        return "/static/img/ChatGPT Image 27 أغسطس 2025، 06_49_51 م.png"


def is_pdf_url_ok(pdf_url: str) -> bool:
    try:
        # فحص سريع بالـ HEAD أولًا لو متاح
        h = requests.head(pdf_url, timeout=15, allow_redirects=True)
        ctype = h.headers.get("Content-Type", "").lower()
        if "pdf" not in ctype:
            # بعض السيرفرات لا تدعم HEAD جيدًا — نجرب GET صغير
            g = requests.get(pdf_url, stream=True, timeout=20)
            ctype = g.headers.get("Content-Type", "").lower()
            first = next(g.iter_content(4096), b"")
            size_header = int(g.headers.get("Content-Length", 0))
            g.close()
            if b"%PDF" not in first[:10] and "pdf" not in ctype:
                return False
            if size_header and size_header < 20 * 1024:
                return False
        return True
    except Exception as e:
        print(f"⚠️ فحص رابط PDF فشل: {e}")
        return False


def download_pdf(pdf_url: str, title: str) -> str | None:
    if not is_pdf_url_ok(pdf_url):
        return None
    try:
        fname = sanitize_filename(title) + ".pdf"
        path = os.path.join(BOOK_DIR, fname)
        with requests.get(pdf_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = 0
            with open(path, "wb") as f:
                for chunk in r.iter_content(1024 * 64):
                    if not chunk:
                        continue
                    f.write(chunk)
                    total += len(chunk)
        if total < 20 * 1024:
            # ملف صغير جدًا → يعتبر تالف
            os.remove(path)
            return None
        return fname
    except Exception as e:
        print(f"❌ تحميل PDF فشل: {e}")
        return None


def insert_book_sqlite(data: dict) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # عدم تكرار الاسم
        cur.execute("SELECT id FROM Books WHERE name=?", (data["name"],))
        if cur.fetchone():
            conn.close()
            print(f"⏭️ مكرر: {data['name']}")
            return False
        cur.execute("SELECT COALESCE(MAX(id),0) FROM Books")
        new_id = cur.fetchone()[0] + 1
        cur.execute(
            """
            INSERT INTO Books (id, name, user_id, author, type, price, branch_id, info, photo_url, more_info, book_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id,
                data["name"],
                None,
                data.get("author", "Unknown"),
                data.get("type", "General"),
                data.get("price", random.randint(80, 250)),
                1,
                data.get("info", ""),
                data.get("photo_url", "default.jpg"),
                data.get("more_info", ""),
                data.get("book_url", ""),
            ),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ إدخال قاعدة البيانات فشل: {e}")
        return False


# ================= منطق OpenLibrary =================

SEARCH_URL = "https://openlibrary.org/search.json"


def search_openlibrary(query: str, limit: int):
    params = {
        "q": query,
        "has_fulltext": "true",
        "public_scan": "true",  # فقط الكتب العامة اللي لها مسح متاح
        "fields": "key,title,author_name,cover_i,ia,public_scan_b",
        "limit": max(limit * 3, limit),  # نجيب أكتر شوية ثم نفلتر
    }
    data = http_get_json(SEARCH_URL, params)
    if not data:
        return []
    return data.get("docs", [])


def pick_pdf_candidates(docs):
    """فلترة النتائج لاختيار ما لديه PDF مباشر عبر archive.org"""
    for d in docs:
        ia_list = d.get("ia") or []
        public = d.get("public_scan_b")
        if not ia_list or not public:
            continue
        ocaid = ia_list[0]
        pdf_url = f"https://archive.org/download/{ocaid}/{ocaid}.pdf"
        yield d, pdf_url


def build_and_save_book(doc, pdf_url):
    title = doc.get("title", "No Title").strip()
    authors = ", ".join(doc.get("author_name", [])[:3]) or "Unknown"
    cover = cover_url_from_id(doc.get("cover_i"))
    work_key = doc.get("key", "")  # مثال: "/works/OL12345W"
    full_desc = fetch_description(work_key) if work_key else ""
    short_desc = (full_desc or title)[:300]

    # نزّل الصورة
    photo_url = save_image(cover, title) if cover else "default.jpg"

    # نزّل PDF (نتأكد إنه سليم)
    book_file = download_pdf(pdf_url, title)
    if not book_file:
        print(f"[SKIP] فشل تنزيل أو تحقق PDF: {title}")
        return False

    data = {
        "name": title,
        "author": authors,
        "type": "General",
        "price": random.randint(80, 250),
        "info": short_desc,
        "photo_url": photo_url,
        "more_info": full_desc or short_desc,
        "book_url": book_file,
    }
    if insert_book_sqlite(data):
        print(f"✅ تم حفظ: {title}")
        return True
    return False


# ================= البرنامج الرئيسي =================
if __name__ == "__main__":
    print("اختر المصدر:")
    print("1 - بحث بكلمة مفتاحية (مع فلترة PDF العام)")
    print("2 - مواضيع جاهزة (science/history/fiction/technology/art)")
    mode = input("اكتب 1 أو 2: ").strip()

    if mode == "2":
        topic = input("ادخل موضوع (science/history/fiction/technology/art): ").strip() or "science"
        query = f"subject:{topic}"
    else:
        query = input("ادخل كلمة البحث: ").strip()

    try:
        limit = int(input("كم كتاب تريد تنزيله (سيتم تخطي ما لا يحتوي PDF)؟ ").strip())
    except Exception:
        limit = 5

    docs = search_openlibrary(query, limit)
    saved = 0
    for doc, pdf_url in pick_pdf_candidates(docs):
        if saved >= limit:
            break
        ok = build_and_save_book(doc, pdf_url)
        if ok:
            saved += 1
        time.sleep(1)

    print(f"\n✅ الانتهاء: تم تنزيل وتخزين {saved} / {limit} كتاب لديه PDF عام صالح.")


    #cd "c:\my\Projectes\Summer Proejct (SP)\Main Fill of SP"

#C:\Users\mohma\PycharmProjects\PythonProject4\.venv\Scripts\activate

#python web_scriping.py