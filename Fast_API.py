from flask import Flask,render_template,jsonify,request,send_file,redirect,session,flash,url_for
import sqlite3
import Book
import Gmail_Sender
import Data_base
import user
import os
from werkzeug.utils import secure_filename
import uuid
import time
import librarian
import stuff
import manager
app=Flask(__name__)
app.secret_key = 'MohmadAyman123'
@app.route("/")
def HomePage():
    is_logged_in = session.get('logged_in', False)
    user_id = session.get("ID")
    state_user=session.get("state")
    photo_url = user.User().get_photo_url(user_id,state_user) if user_id else None
    return render_template("HomePage.html",
                           title="HomePage",
                           custom_css='homepage',
                           books=get_all_book(),
                           custom_js='homepage',
                            log_in_flage=is_logged_in,
                            photo_url=photo_url,
                            state_user=state_user,
                            chat_enabled=1
    )


def get_all_book():
    Vild_data=Book.Book().all_book()
    new_data=Vild_data[0]
    result=[{"name_book": row[0], "author": row[1].strip(), "price":row[2], "branch_id":row[3], "info":row[4], "photo_url":row[5], "id":row[6], "more_info":row[7], "book_url":row[8]} for row in new_data]
    return result


@app.route("/api/subscribe", methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"status": "error", "message": "البريد الإلكتروني مطلوب"}), 400

    Gmail_Sender.gmail().send_new_update(email)

    return jsonify({
        "status": "success",
        "message": "تم الاشتراك بنجاح!",
        "email": email
    }), 200



@app.route('/api/search/suggestions')
def search_suggestions():
    query = request.args.get('q', '').lower()
    books = get_all_book() 
    
    suggestions = [book for book in books if query in book['name_book'].lower()]
    return jsonify([{'name_book': book['name_book']} for book in suggestions[:5]])

@app.route('/api/search')
def search_books():
    query = request.args.get('q', '').lower()
    books = get_all_book()
    
    results = [book for book in books if query in book['name_book'].lower()]
    
    return jsonify(results)



@app.route('/api/books')
def get_books():
    page = request.args.get('page', default=1, type=int)
    per_page = 36 
    
    all_books = get_all_book()

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    paginated_books = all_books[start_idx:end_idx]
    
    return jsonify({
        "books": paginated_books,
        "current_page": page,
        "total_pages": (len(all_books) + per_page - 1),
        })

@app.route("/book/<int:book_id>")
def book_details(book_id):
    all_books = get_all_book()
    book = next((book for book in all_books if book['id'] == book_id), None)
    is_logged_in = session.get('logged_in', False)
    user_id = session.get("ID")
    user_rating = None
    photo_url = user.User().get_photo_url(user_id, session["state"]) if user_id else None

    if not book:
        return render_template("404.html"), 404

    if is_logged_in and user_id:

        user_rating = Book.Book().get_user_rating(user_id,book_id)

    return render_template("BookDetails.html",
                           title=book['name_book'],
                           book=book,
                           custom_css='BookPage',
                           books=get_all_book(),
                           custom_js='BookPage',
                           log_in_flage=is_logged_in,
                           photo_url=photo_url,
                           rating=user_rating 
                           )



@app.route("/rate-book/<int:book_id>", methods=["POST"])
def rate_book(book_id):
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 403

    user_id = session.get("ID")
    data = request.get_json()
    try:
        rating_value = int(data.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid rating format"}), 400

    if not (1 <= rating_value <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    db = Book.Book()
    db.insert_rating(user_id, book_id, rating_value)

    return jsonify({"success": True})


from flask import send_from_directory
import os

UPLOAD_FOLDER1 = os.path.join(app.root_path, 'static', 'Books')

@app.route('/download/<int:book_id>')
def download_file(book_id):
    book_url = Data_base.Data_Base()._get_url2(id=book_id)

    if not book_url or not book_url[0][0]:
        return "الكتاب غير متاح للتحميل", 404

    filename = os.path.basename(book_url[0][0])

    file_path = os.path.join(UPLOAD_FOLDER1, filename)
    print(f"[DEBUG] Full path: {file_path}")

    if not os.path.exists(file_path):
        return "ملف الكتاب غير موجود", 404
    Book.Book().add_my_books(session["ID"],book_id,2)
    return send_from_directory(
        UPLOAD_FOLDER1,
        filename,
        as_attachment=True
    )

BOOKS_FOLDER = 'static/Books'

@app.route('/view/<int:book_id>')
def view_book(book_id):
    book_data = Data_base.Data_Base()._get_url2(id=book_id)
    
    if not book_data or not book_data[0][0]:
        return "الكتاب غير متاح للقراءة", 404
    filename = os.path.basename(book_data[0][0])
    file_path = os.path.join(BOOKS_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return "ملف الكتاب غير موجود", 404
    
    return send_file(file_path, mimetype='application/pdf')

@app.route('/add_to_library/<int:book_id>', methods=['POST'])
def add_to_library(book_id):
    user_id = session.get("ID")
    if not user_id:
        return redirect('/login')

    result = Book.Book().add_my_books(user_id, book_id, 1)  # استدعاء الفانكشن اللي عندك
    if result == 1:
        flash("تمت إضافة الكتاب إلى مكتبتك بنجاح")
    else:
        flash("حدث خطأ أثناء الإضافة")

    return redirect(request.referrer)  # يرجع لنفس الصفحة

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ID_state = user.User().Log_in(username, password)
        if ID_state==0:
            return render_template("login.html", error="كلمة المرور غير صحيحة", custom_css='login')
        if ID_state[1] == 1:
            session['logged_in'] = True
            session['ID'] = ID_state[0]
            print("user")
            session["state"]=ID_state[1]
            return redirect("/")

        elif ID_state[1] == 2:
            session['logged_in'] = True
            session['ID'] = ID_state[0]
            session["state"]=ID_state[1]
            print("librarian")
            return redirect("/")

        elif ID_state[1] == 3:
            session['logged_in'] = True
            session['ID'] = ID_state[0]
            session["state"]=ID_state[1]
            print("manager")
            return redirect("/")

            

    return render_template("login.html", custom_css='login')

@app.route("/")
def api_user():
    return jsonify(get_all_book())


@app.route("/Favorite_list")
def Favorite_list():
    user_id=session["ID"]
    data_list=Book.Book().get_my_books(user_id,1)
    photo_url=user.User().get_photo_url(session["ID"],session["state"])
    book=Book.Book().get_custom_book(data_list)
    if not session.get('logged_in'):
        return redirect('/login?next=/account')
    else:
        return(render_template("Favorite list.html",photo_url=photo_url,custom_css='account',books=book))

@app.route("/Download_list")
def Download_list():
    user_id=session["ID"]
    data_list=Book.Book().get_my_books(user_id,2)
    photo_url=user.User().get_photo_url(session["ID"],session["state"])
    book=Book.Book().get_custom_book(data_list)
    if not session.get('logged_in'):
        return redirect('/login?next=/account')
    else:
        return(render_template("Favorite list.html",photo_url=photo_url,custom_css='account',books=book))

@app.route("/get_top_books")
def get_top_books():
    books = Book.Book().get_top_book()
    return jsonify(books)


@app.route("/logout")
def logout():
    session["state"]=0
    session.pop('logged_in', None)
    return redirect("/")

@app.route('/account')
def account():
    state_user=session.get("state")
    photo_url=user.User().get_photo_url(session["ID"],session["state"])
    if not session.get('logged_in'):
        return redirect('/login?next=/account')
    return render_template('account.html',photo_url=photo_url,custom_js='account',custom_css='account',
                           state_user=state_user
                           )



UPLOAD_FOLDER = 'static/photo_user'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/update_info', methods=['GET', 'POST'])
def update_info():
    user_id = session.get("ID")
    state_user = session.get("state")
    errors = {}

    if not user_id or not state_user:
        flash("You must be logged in to access this page.", "danger")
        return redirect(url_for("login"))

    user_obj = user.User()
    data_user = user_obj.user_info(state_user, user_id)

    first_name = data_user.get("first_name", "")
    last_name = data_user.get("l_name", "")
    email = data_user.get("email", "")
    photo_url = user_obj.get_photo_url(user_id, state_user)

    if request.method == 'POST':
        username = request.form.get("username", "").strip()
        new_email = request.form.get("email", "").strip()
        old_password = request.form.get("old_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        has_changes = False

        if username:
            name_parts = username.split()
            new_first_name = name_parts[0]
            new_last_name = name_parts[1] if len(name_parts) > 1 else ""

            if new_first_name != first_name:
                user_obj.update_user_first_name(user_id, new_first_name)
                has_changes = True

            if new_last_name != last_name:
                user_obj.update_user_last_name(user_id, new_last_name)
                has_changes = True

        if new_email and new_email != email:
            if "@" not in new_email:
                errors["email"] = "Invalid email format."
            else:
                user_obj.update_user_email(user_id, new_email, ver_code=None)
                has_changes = True

        if new_password or confirm_password:
            if not old_password:
                errors["old_password"] = "Current password is required."
            elif new_password != confirm_password:
                errors["confirm_password"] = "Passwords do not match."
            elif len(new_password) < 9:
                errors["new_password"] = "Password must be at least 9 characters."
            else:
                if user_obj.update_user_password(user_id, old_password, new_password):
                    has_changes = True
                else:
                    errors["old_password"] = "Current password is incorrect."

        UPLOAD_FOLDER = 'static/photo_user'
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        file = request.files.get('profile_picture')
        if file and allowed_file(file.filename):
            filename = f"{user_id}.png"  
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            user_obj.update_photo_url(user_id, f"/{file_path}", state_user)
            has_changes = True

        if has_changes and not errors:
            flash("Account info updated successfully.", "success")
            return redirect(url_for("account"))

        first_name = username
        email = new_email

    return render_template(
        'update_info.html',
        title="Account",
        photo_url=photo_url,
        custom_css='update_info',
        user={"username": first_name + " " + last_name, "email": email},
        errors=errors,
        state_user=state_user
    )
@app.route("/create_account", methods=["GET", "POST"])
def create_account_route():
    state_user = session.get("state")
    manager_ids = manager.Manager().managers_ids()
    library_num = manager.Manager().library_num()
    show_verification = False
    result = None
    user_obj = user.User()

    if request.method == "POST":
        step = request.form.get("step", "1")

        if state_user == 3:
            if step == "1":
                print("STEP MANAGER")
                session["user_data"] = {
                    "username": request.form.get("username"),
                    "password": request.form.get("password"),
                    "salary": request.form.get("salary"),
                    "phone": request.form.get("phone"),
                    "f_name": request.form.get("first_name"),
                    "l_name": request.form.get("last_name"),
                    "manager_id": request.form.get("manager_id"),
                    "library_id": request.form.get("library_id"),
                }
                user_data = session.get("user_data", {})

                
                if user_obj.check_info_dub_send(phone=user_data["phone"]) == 1:
                    result = manager.Manager()._add_new_librarian(user_data)
                    session['logged_in'] = True
                    flash("The account has been activated. ")
                    return render_template("HomePage.html",
                           state_user=state_user,
                           result=result,
                           manager_ids=manager_ids,
                           library_num=library_num,
                           show_verification=show_verification,
                           custom_css='homepage',
                           custom_js='homepage',
                           )
                else:
                    flash("Phone already exists")

        elif step == "1":
            print("STEP ONE")
            session["user_data"] = {
                "username": request.form.get("username"),
                "password": request.form.get("password"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "type_user": request.form.get("type_user"),
            }
            user_data = session.get("user_data", {})
            show_verification = True

            if user_obj.check_info_dub_send(user_data["email"], user_data["phone"]) == 1:
                return render_template("create_account.html", show_verification=True, custom_css='create_account')
            else:
                flash("Email or phone already exists")

        elif step == "2":
            print("STEP TWO")
            user_data = session.get("user_data", {})
            verification_code = request.form.get("verification_code")

            if user_obj.check_ver_code(verification_code):
                result = user.User().create_account(
                    user_data["username"],
                    user_data["password"],
                    user_data["email"],
                    user_data["phone"],
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["type_user"],
                )
                session['logged_in'] = True
                return redirect(url_for('HomePage'))
            else:
                flash("Something is wrong")

    return render_template("create_account.html",
                           state_user=state_user,
                           manager_ids=manager_ids,
                           library_num=library_num,
                           show_verification=show_verification,
                           custom_css='create_account')




UPLOAD_FOLDER3 = 'static/Books'
ALLOWED_EXTENSIONS = {'pdf','png','jpg', 'jpeg', 'gif', 'webp','bmp','tiff' }
UPLOAD_IMG='static/img' 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER3
app.config['UPLOAD_IMG'] = UPLOAD_IMG
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/add-book")
def add_book_page():
    if session.get('state')==2 or session.get('state')==3:
        return render_template("add-book.html", custom_css='add-book')
    else:
        return redirect(url_for("login"))
    
@app.route("/api/add_book", methods=["POST"])
def api_add_book():
    if session.get('state')==2:
        try:

            if 'book_file' not in request.files or 'book_image' not in request.files:
                flash('The required files were not selected', 'error')
                return redirect(url_for("add_book_page"))
            
            book_file = request.files['book_file']
            book_image = request.files['book_image']
            

            if book_file.filename == '' or book_image.filename == '':
                flash('only PDF', 'error')
                return redirect(url_for("add_book_page"))

            if not (book_file and allowed_file(book_file.filename)):
                flash('only PDF', 'error')
                return redirect(url_for("add_book_page"))
            

            if not (book_image and allowed_file(book_image.filename)):
                flash('The book image format is not allowed. Please upload an image.(png, jpg, jpeg, gif)', 'error')
                return redirect(url_for("add_book_page"))
            

            book_filename = secure_filename(book_file.filename)
            image_filename = secure_filename(book_image.filename)
            

            
            book_path = os.path.join(app.config['UPLOAD_FOLDER'], book_filename)
            image_path = os.path.join(app.config['UPLOAD_IMG'], image_filename)

            book_file.save(book_path)
            book_image.save(image_path)
            

            book_url = book_filename
            image_url = f"/static/img/{image_filename}"
            

            dic_data = {
                "name": request.form.get("name"),
                "user_id": None, 
                "author": request.form.get("author"),
                "type": request.form.get("type"),
                "price": request.form.get("price"),
                "branch_id": 1,
                "info": request.form.get("info"),
                "photo_url": image_url, 
                "more_info": request.form.get("more_info"),
                "book_url": book_url,
            }
            

            result = librarian.Librarian().add_new_book(dic_data)
            
            if result == 1:
                flash("The book has been added successfully.", 'success')
                return redirect(url_for("add_book_page"))
            else:
                flash("Try Agian", 'error')
                return redirect(url_for("add_book_page"))
                
        except Exception as e:
            flash("Try Agian", 'error')
            return redirect(url_for("add_book_page"))
    else:
        return redirect(url_for("login"))

@app.route("/remove-book")
def remove_book():
    if session.get('state')==2 or  session.get('state')==3:
        is_logged_in = session.get('logged_in', False)
        user_id = session.get("ID")
        state_user=session.get("state")
        photo_url = user.User().get_photo_url(user_id,state_user) if user_id else None

        return render_template("Remove_book.html",
                            title="Remove Books",
                            custom_css='homepage',
                            books=get_all_book(),
                            custom_js='Remove-book',
                                log_in_flage=is_logged_in,
                                photo_url=photo_url,
                                state_user=state_user
        )
    else:
        return redirect(url_for("login")) 

@app.route("/del-book/<int:book_id>")
def del_book(book_id):
    if session['state']==2:
        stuff.Stuff().remove_book(book_id)
        flash("تم حذف الكتاب بنجاح", "success")
        return redirect(url_for("remove_book"))
    else:
        return redirect(url_for("login")) 



@app.route("/edit-book")
def edit_book():
    if session['state']==2:
        is_logged_in = session.get('logged_in', False)
        user_id = session.get("ID")
        state_user=session.get("state")
        photo_url = user.User().get_photo_url(user_id,state_user) if user_id else None
        return render_template("edit-book.html",
                            title="Edit Books",
                            custom_css='homepage',
                            books=get_all_book(),
                            custom_js='edit-book',
                            log_in_flage=is_logged_in,
                            photo_url=photo_url,
                            state_user=state_user
        )
    else:
        return redirect(url_for("login")) 



@app.route("/edit-book/<int:book_id>",methods=["GET", "POST"])
def edit_book_id(book_id):
    if session['state']==2:
        all_books = get_all_book()
        book = next((book for book in all_books if book['id'] == book_id), None)
        is_logged_in = session.get('logged_in', False)
        user_id = session.get("ID")
        user_rating = None
        photo_url = user.User().get_photo_url(user_id, session["state"]) if user_id else None

        if not book:
            return render_template("404.html"), 404
        if request.method == "POST":
                name_book = request.form.get("name_book")
                author = request.form.get("author")
                price = request.form.get("price")
                more_info = request.form.get("more_info")
                data_dic={'name_book':name_book,'author':author,'price':price,'more_info':more_info}
                Book.Book().update_book(book_id,data_dic)

                flash("Book updated successfully", "success")
                return redirect(url_for("edit_book_id", book_id=book_id))
        

        return render_template("edit-bookdetails.html",
                            title=book['name_book'],
                            book=book,
                            custom_css='BookPage',
                            books=get_all_book(),
                            custom_js='BookPage',
                            log_in_flage=is_logged_in,
                            photo_url=photo_url,
                            rating=user_rating 
                            )

    else:
        return redirect(url_for("login")) 
@app.route("/update-book/<int:book_id>", methods=["POST"])
def update_data(book_id):
    name_book = request.form.get("name_book")
    author = request.form.get("author")
    price = request.form.get("price")
    more_info = request.form.get("more_info")
    data_dic={'name_book':name_book,'author':author,'price':price,'more_info':more_info}
    Book.Book().update_book(book_id,data_dic)

    flash("Book updated successfully", "success")
    return redirect(url_for("edit_book_id", book_id=book_id))


@app.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html",
                           custom_css='homepage',
                           custom_js='homepage'
                           )

@app.route("/DashBoard")
def DashBoard():
        if session['state']==3:
            data_dic=Book.Book().DashBoard_data()
            books = list(zip(data_dic['id'], data_dic['names'], data_dic['num_down']))
            data_dic_extra_4=Book.Book().DashBoard_data(status=4)
            data_dic_extra_1=Book.Book().DashBoard_data(status=1)
            data_dic_extra_2=Book.Book().DashBoard_data(status=2)
            data_dic_extra_3=Book.Book().DashBoard_data(status=3)
            print(data_dic)
            return render_template("DashBoard.html",
                            custom_css='DashBoard',
                            books=books,
                            data_dic_extra=data_dic_extra_4,
                            data_dic_extra_1=data_dic_extra_1,
                            data_dic_extra_2=data_dic_extra_2,
                            data_dic_extra_3=data_dic_extra_3
                            )
        else:
            return redirect(url_for("login")) 
        

@app.route('/Remove_u_l')
def user_data():

    users=Data_base.Data_Base().get_user_librarian_data(user_id=1,librarian_id=1)
    is_logged_in = session.get('logged_in', False)
    user_id = session.get("ID")
    state_user=session.get("state")
    photo_url = user.User().get_photo_url(user_id,state_user) if user_id else None
    print(users)
    return render_template('Remove_u_l.html', users=users,title="Remove_user_librarian",
                           custom_css='homepage',
                           custom_js='homepage',
                            log_in_flage=is_logged_in,
                            photo_url=photo_url,
                            state_user=state_user,)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    # تحقق من نوع الـ user_id (هل هو مستخدم أم أمين مكتبة)
    user_type = Data_base.Data_Base().get_user_type(user_id)
    
    # حذف البيانات بناءً على النوع
    if user_type == "librarian":
        Data_base.Data_Base().remove_l_u(librarian_id=user_id)
        flash("تم حذف أمين المكتبة بنجاح!", "success")
    elif user_type == "user":
        Data_base.Data_Base().remove_l_u(user_id=user_id)
        flash("تم حذف المستخدم بنجاح!", "success")
    else:
        flash("المستخدم غير موجود في النظام.", "error")

    return redirect(url_for('user_data'))

if __name__=="__main__":
    app.run(debug=True,port=9000,host='0.0.0.0')



