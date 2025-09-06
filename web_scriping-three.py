import os
import re
import sqlite3
import time
import random
import requests
from PIL import Image
from io import BytesIO
import librarian
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin

# ---------- الإعدادات ----------
EMAIL = "mohmadweee75@gmail.com"
PASSWORD = "01006658620"
IMG_DIR = r"C:\my\Projectes\Summer Proejct (SP)\Main Fill of SP\static\img"
BOOK_DIR = r"C:\my\Projectes\Summer Proejct (SP)\Main Fill of SP\static\Books"
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "library_DB.db")

DB_PATH = db_path
EDGE_DRIVER_PATH = r"C:\DRIVERS\msedgedriver.exe"

# ---------- تنظيف اسم الملف ----------
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|()\']', "_", name).replace(" ", "_")

# ---------- إعداد المتصفح ----------
options = Options()
prefs = {
    "download.default_directory": BOOK_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True
}
options.add_experimental_option("prefs", prefs)
service = Service(executable_path=EDGE_DRIVER_PATH)
driver = webdriver.Edge(service=service, options=options)

# ---------- فتح الموقع ----------
print("🔎 فتح الموقع: Ketabpedia")
driver.get("https://ketabpedia.com/")
time.sleep(3)

# ---------- طلب اسم الكتاب من المستخدم ----------
book_name = input("من فضلك، ادخل اسم الكتاب الذي ترغب في البحث عنه: ")

# ---------- البحث عن الكتاب ----------
print("🔍 البحث عن الكتاب...")
search_box = driver.find_element(By.CSS_SELECTOR, ".elementor-search-form__input")
search_box.send_keys(book_name)  # اسم الكتاب الذي تم إدخاله
search_box.send_keys(Keys.RETURN)  # الضغط على زر البحث
time.sleep(5)
print("✅ تم إدخال الكلمة في مربع البحث.")

# ---------- التمرير لأسفل لتحميل المزيد من الكتب ----------
print("🔽 التمرير لأسفل لتحميل المزيد من الكتب...")
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)  # انتظار تحميل المزيد من العناصر

# ---------- الانتظار حتى تظهر روابط الكتب ----------
print("⏳ انتظار تحميل روابط الكتب...")
try:
    book_elements = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.elementor-loop-item"))
    )
    if not book_elements:
        print("⚠️ لم يتم العثور على أي كتب في نتائج البحث.")
    else:
        print(f"تم العثور على {len(book_elements)} كتاب في الصفحة.")
except Exception as e:
    print(f"❌ فشل في العثور على روابط الكتب: {e}")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

num_books = int(input(":كم عدد الكتب التي تريد تحميلها؟ "))
downloaded = 0
book_index = 0

while downloaded < num_books and book_index < len(book_elements):
    book_link = book_elements[book_index]
    book_index += 1

    try:
        # استخراج رابط الكتاب وصورة الغلاف
        print("🔄 استخراج رابط الكتاب وصورة الغلاف...")
        link_tag = book_link.find_element(By.CSS_SELECTOR, "a")
        book_url = link_tag.get_attribute("href")
        image_url = book_link.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
        title = book_link.find_element(By.CSS_SELECTOR, ".elementor-heading-title").text.strip()
        author = "غير معروف"  # يمكن تعديل هذه النقطة حسب الحاجة

        print(f"\n⬇️ جاري معالجة: {title} / {author}")
        print(f"📎 رابط الكتاب: {book_url}")

        driver.execute_script("window.open(arguments[0]);", book_url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        # استخراج صورة الغلاف
        print("📸 استخراج صورة الغلاف...")
        try:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            image_filename = f"{sanitize_filename(title)}_{random.randint(1000, 9999)}.jpg"
            img_path = os.path.join(IMG_DIR, image_filename)
            image.save(img_path)
            img_url_db = f"/static/img/{image_filename}"
            print(f"✅ تم تحميل صورة الغلاف: {img_url_db}")
        except Exception as e:
            print(f"⚠️ لم يتم تحميل صورة الغلاف: {e}")
            img_url_db = "/static/img/default_image.jpg"  # صورة افتراضية

        # استخراج رابط تحميل PDF
        print("📥 استخراج رابط تحميل PDF...")
        try:
            pdf_url = None
            pdf_button = driver.find_element(By.XPATH, "//a[contains(@href, '/تحميل/')]")
            pdf_url = pdf_button.get_attribute("href")
            print(f"📥 رابط تحميل PDF: {pdf_url}")

            # تحميل الـ PDF
            print("📥 تحميل الكتاب PDF...")
            book_filename = f"{sanitize_filename(title)}_{random.randint(1000, 9999)}.pdf"
            book_path = os.path.join(BOOK_DIR, book_filename)
            response = requests.get(pdf_url)
            with open(book_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ تم تحميل الكتاب: {title}")
        except Exception as e:
            print(f"⚠️ لم يتم العثور على رابط تحميل PDF: {e}")

        # إضافة البيانات إلى قاعدة البيانات
        print("💾 إضافة البيانات إلى قاعدة البيانات...")
        cursor.execute("SELECT MAX(id) FROM Books")
        max_id = cursor.fetchone()[0]
        new_id = max_id + 1 if max_id else 1
        data_dic = {
            "name": title,
            "user_id": new_id,
            "author": author,
            "type": "General",
            "price": random.randint(80, 250),
            "branch_id": 1,
            "info": "معلومات الكتاب...",
            "photo_url": img_url_db,
            "more_info": "معلومات إضافية عن الكتاب...",
            "book_url": book_filename
        }
        librarian.Librarian().add_new_book(data_dic)

        downloaded += 1
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        continue

# ---------- النهاية ----------
print(f"✅✅ تم الانتهاء من تحميل وحفظ {downloaded} من أصل {num_books} كتب.")
driver.quit()
conn.close()
