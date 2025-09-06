import os
import re
import sqlite3
import time
import random
import requests
from PIL import Image
from io import BytesIO
import librarian
from bs4 import BeautifulSoup
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

# ---------- تسجيل الدخول ----------
driver.get("https://en.z-library.sk/")
time.sleep(3)
driver.find_element(By.XPATH, "/html/body/div[1]/div/nav/section[2]/a").click()
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/input').send_keys(EMAIL)
pw_input = driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/input')
pw_input.send_keys(PASSWORD)
pw_input.send_keys(Keys.ENTER)
time.sleep(5)

# ---------- فتح صفحة التوصيات ----------
driver.get("https://z-library.sk/users/zrecommended#18237644,18237419,5915211,1048267,23567127,23567119,23567130,23567115,23567117,23567143,29609753,1077079,18240675,29605075,29423930,1086204")
time.sleep(5)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

num_books = int(input(":كم عدد الكتب التي تريد تحميلها؟ "))
book_elements = driver.find_elements(By.CSS_SELECTOR, "a.item")
print(f"\U0001F4DA تم العثور على {len(book_elements)} كتاب في الصفحة.")

downloaded = 0
book_index = 0

while downloaded < num_books and book_index < len(book_elements):
    book_link = book_elements[book_index]
    book_index += 1

    try:
        z_cover = book_link.find_element(By.TAG_NAME, "z-cover")
        title = z_cover.get_attribute("title") or "NoTitle"
        author = z_cover.get_attribute("author") or "NoAuthor"
        href = book_link.get_attribute("href")
        book_url = href if href.startswith("http") else "https://en.z-library.sk" + href

        print(f"\n⬇️ جاري معالجة: {title} / {author}")
        print(f"📎 رابط الكتاب: {book_url}")

        driver.execute_script("window.open(arguments[0]);", book_url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        title_tag = soup.find("h1", class_="book-title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        cursor.execute("SELECT 1 FROM Books WHERE name = ?", (title,))
        if cursor.fetchone():
            print(f"⏩ تم تخطي الكتاب لأنه محفوظ مسبقًا: {title}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

        safe_title = sanitize_filename(title)

        description_block = soup.find("div", id="bookDescriptionBox")
        full_info = short_info = """This book offers an engaging and insightful exploration of its subject, 
                                providing readers with valuable knowledge and inspiration. 
                                It is suitable for both beginners and those with prior experience, 
                                making it a worthwhile addition to any collection."""
        if description_block:
            for br in description_block.find_all("br"):
                br.replace_with("\n")
            full_info = description_block.get_text(separator='\n', strip=True)
            sentences = re.split(r'(?<=[.!؟؛])\s+', full_info.strip())
            short_info = sentences[0] if sentences else full_info[:150]

        genre_block = soup.find("div", class_="bookProperty property__tags")
        book_type = "General"
        if genre_block:
            book_type = genre_block.get_text(strip=True).replace("Tags:", "")

        # -------- صورة الغلاف --------
        # -------- تحميل صورة الغلاف --------
        try:
            # المحاولة الأولى مع img.image.cover
            try:
                z_cover = driver.find_element(By.TAG_NAME, "z-cover")
                shadow_root = driver.execute_script("return arguments[0].shadowRoot", z_cover)
                img_element = shadow_root.find_element(By.CSS_SELECTOR, "img.image.cover")
                image_url = img_element.get_attribute("src")
                print(f"✅ رابط الصورة (cover): {image_url}")
            except:
                # إذا فشلت المحاولة الأولى، جرب img.image
                z_cover = driver.find_element(By.TAG_NAME, "z-cover")
                shadow_root = driver.execute_script("return arguments[0].shadowRoot", z_cover)
                img_element = shadow_root.find_element(By.CSS_SELECTOR, "img.image")
                image_url = img_element.get_attribute("src")
                print(f"✅ رابط الصورة (image): {image_url}")

            # تحميل الصورة
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            image_filename = f"{safe_title[:120]}_{random.randint(1000,9999)}.jpg"
            img_path = os.path.join(IMG_DIR, image_filename)
            image.save(img_path)
            img_url_db = f"/static/img/{image_filename}"

        except Exception as e:
            print(f"⚠️ لم يتم تحميل صورة الغلاف: {e}")
            img_url_db = "/static/img/ChatGPT Image 27 أغسطس 2025، 06_49_51 م.png"


        # -------- رابط التحميل PDF --------
        # -------- رابط التحميل PDF --------
        # -------- رابط التحميل PDF --------
        try:
            pdf_url = None  # ← تعريف مبدأي قبل أي محاولة

            # محاولة أولى: تحقق من الزر الرئيسي إن كان فيه رابط PDF
            try:
                main_btn = driver.find_element(By.CSS_SELECTOR, "a.addDownloadedBook")
                main_href = main_btn.get_attribute("href")

                ext_span = main_btn.find_element(By.CSS_SELECTOR, "span.book-property__extension")
                file_ext = ext_span.text.strip().lower()

                if main_href and "/dl/" in main_href and file_ext == "pdf":
                    pdf_url = urljoin("https://en.z-library.sk", main_href)
                    print(f"📥 رابط PDF (من الزر الرئيسي): {pdf_url}")
                else:
                    print(f"ℹ️ الزر الرئيسي ليس بصيغة PDF (الصيغة: {file_ext})، سيتم تجربة القائمة المنسدلة.")
            except Exception as e:
                print(f"⚠️ لم يتم العثور على زر التحميل الرئيسي أو لم يحتوي على PDF: {e}")

            # محاولة ثانية: استخدام القائمة المنسدلة إذا لم نجد PDF في الزر الرئيسي
            if not pdf_url:
                try:
                    dropdown_btn = driver.find_element(By.ID, "btnCheckOtherFormats")
                    dropdown_btn.click()
                    time.sleep(2)
                    pdf_links = driver.find_elements(By.CSS_SELECTOR, "ul.dropdown-menu a")

                    for link in pdf_links:
                        text = link.text.strip().lower()
                        href = link.get_attribute("href")
                        if "pdf" in text and "/dl/" in href:
                            pdf_url = urljoin("https://en.z-library.sk", href)
                            print(f"📥 رابط PDF (من القائمة): {pdf_url}")
                            break

                    if not pdf_url:
                        print(f"⚠️ لا يوجد رابط تحميل PDF داخل القائمة، سيتم تخطي الكتاب.")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue
                except Exception as e:
                    print(f"⚠️ لم يتم العثور على زر الثلاث نقاط أو روابط PDF: {e}")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

            # تحميل الملف
            book_filename = f"{safe_title}_{random.randint(1000,9999)}.pdf"[:100]
            book_path = os.path.join(BOOK_DIR, book_filename)

            try:
                before_files = set(os.listdir(BOOK_DIR))
                driver.get(pdf_url)
                
                # الانتظار الذكي لاكتمال التحميل
                max_wait_time = 300  # زيادة وقت الانتظار إلى 5 دقائق
                start_time = time.time()
                last_size = 0
                stable_count = 0
                new_file = None
                
                while True:
                    time.sleep(5)
                    after_files = set(os.listdir(BOOK_DIR))
                    
                    # البحث عن أي ملف جديد (سواء .pdf أو .crdownload)
                    temp_new_files = [f for f in after_files - before_files 
                                    if f.lower().endswith(('.pdf', '.crdownload'))]
                    
                    if temp_new_files:
                        new_file = temp_new_files[0]
                        file_path = os.path.join(BOOK_DIR, new_file)
                        
                        try:
                            current_size = os.path.getsize(file_path)
                            
                            # إذا كان الملف قد اكتمل تحميله (لم يعد .crdownload)
                            if not new_file.lower().endswith('.crdownload'):
                                if current_size == last_size:
                                    stable_count += 1
                                    if stable_count >= 2:
                                        break
                                else:
                                    stable_count = 0
                                    last_size = current_size
                            
                            print(f"⏳ جاري التحميل: {new_file} ({current_size/1024/1024:.2f} MB)")
                            
                        except (FileNotFoundError, OSError) as e:
                            print(f"⚠️ خطأ في قراءة الملف: {e}")
                            continue
                    
                    # إذا انتهى وقت الانتظار
                    if time.time() - start_time > max_wait_time:
                        raise Exception(f"انتهى وقت الانتظار ({max_wait_time} ثانية) دون اكتمال التحميل")
                
                if not new_file:
                    raise Exception("⚠️ لم يتم تحميل أي ملف PDF.")
                
                # التأكد من أن الملف النهائي هو PDF
                final_file = new_file.replace('.crdownload', '') if new_file.endswith('.crdownload') else new_file
                if not final_file.lower().endswith('.pdf'):
                    raise Exception(f"⚠️ الملف الذي تم تحميله ليس PDF: {final_file}")
                
                # إعادة تسمية الملف إذا لزم الأمر
                if new_file != final_file:
                    os.rename(os.path.join(BOOK_DIR, new_file), os.path.join(BOOK_DIR, final_file))
                
                os.rename(os.path.join(BOOK_DIR, final_file), book_path)
                print(f"✅ تم تحميل الكتاب وإعادة تسميته: {book_filename} ({last_size/1024/1024:.2f} MB)")

            except Exception as e:
                print(f"❌ فشل في تحميل الكتاب: {e}")
                # تنظيف أي ملفات غير مكتملة
                if 'new_file' in locals() and new_file and os.path.exists(os.path.join(BOOK_DIR, new_file)):
                    try:
                        os.remove(os.path.join(BOOK_DIR, new_file))
                        print(f"🧹 تم تنظيف الملف غير المكتمل: {new_file}")
                    except:
                        pass
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
                if not new_files:
                    raise Exception("⚠️ لم يتم تحميل أي ملف PDF.")

                new_file = new_files.pop()
                if not new_file.lower().endswith(".pdf"):
                    raise Exception(f"⚠️ الملف الذي تم تحميله ليس PDF: {new_file}")

                os.rename(os.path.join(BOOK_DIR, new_file), book_path)
                print(f"✅ تم تحميل الكتاب وإعادة تسميته: {book_filename}")

            except Exception as e:
                print(f"❌ فشل في تحميل الكتاب: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

        except Exception as e:
            print(f"⚠️ خطأ غير متوقع أثناء محاولة الحصول على رابط PDF: {e}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue



        cursor.execute("SELECT MAX(id) FROM Books")
        max_id = cursor.fetchone()[0]
        new_id = max_id + 1 if max_id else 1
        data_dic={"name":title,"user_id":new_id,"author":author,"type":book_type,"price": random.randint(80, 250),"branch_id":1,"info":short_info,"photo_url":img_url_db,"more_info":full_info,"book_url":book_filename}
        librarian.Librarian().add_new_book(data_dic)

        downloaded += 1
        print(f"💾 تم حفظ الكتاب: {title}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        continue

# ---------- النهاية ----------
driver.quit()
conn.close()
print(f"\n✅✅ تم الانتهاء من تحميل وحفظ {downloaded} من أصل {num_books} كتب.")


#cd "c:\my\Projectes\Summer Proejct (SP)\Main Fill of SP"

#C:\Users\mohma\PycharmProjects\PythonProject4\.venv\Scripts\activate

#python web_scriping.py
