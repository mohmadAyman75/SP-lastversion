import sqlite3

import Gmail_Sender
from Gmail_Sender import *
from Data_base import Data_Base
import string
from Book import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
gmail_obj=Gmail_Sender.gmail()
class User(Book,Data_Base):
    
    def __init__(self):
        self.Name=""
        self.ID=0
        self.__Phone=0
        self.__pass=0

    def search(self,Phone_number):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        data=cursor.execute("SELECT phone FROM User WHERE phone=?",(Phone_number,)).fetchall()
        if data:
            return 0
        else:
            return 1

    def get_recent_book(self,ID):
        db=Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        self.ID=ID
        data_dic=[]
        data=cursor.execute("SELECT name FROM Books WHERE user_id = ?",(self.ID,)).fetchall()
        names=[]
        for x in data:
            names.append(x[0])
        if data:
            for x in range(len(names)):
                data_dic.append(names[x])
            return data_dic
        else:
            print("you don`t have any book\nyou can borrow books..\n")
            return data_dic


    def contacnt_support(self):
        data_dic="Contact support by calling this \nnumber:0128107----\nGmail:mohmadwe75@gmail.com\nWhatsApp:0128107----"
        return data_dic

    def info_return_data(self,ID):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        self.ID = ID
        data_dic=[]

        def db():
            book_id=cursor.execute("SELECT books_id FROM Subscription WHERE user_id = ?",(self.ID,)).fetchall()
            update_id=[]
            for x in book_id:
                update_id=[str(item) for item in x]
            book_name=cursor.execute("SELECT name FROM Books WHERE id = ?",(*update_id,)).fetchall()
            dates = cursor.execute("SELECT s_date, e_date FROM Subscription WHERE user_id = ?", (self.ID,)).fetchall()
            names=[];date=[]
            for x in book_name:
                names.append(x[0])
            for x in dates:
                date.append(x)
            if date:
                for x in range(len(names)):
                    data_dic.append((names[0],date[0]))

                return data_dic
            else:
                print("False ID try again\n")
                return data_dic

        db()



    def update_user_email(self,user_id, new_email, ver_code):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        old_email = cursor.execute("SELECT email FROM User WHERE id=?", (user_id,)).fetchone()
        if old_email:
            Gmail_Sender.send_message_random_code(old_email[0])
            if ver_code == random_var():
                cursor.execute("UPDATE User SET email=? WHERE id=?", (new_email, user_id))
                conn.commit()
                return 1
        return 0

    def update_user_first_name(self,user_id, first_name):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        cursor.execute("UPDATE User SET f_name=? WHERE id=?", (first_name, user_id))
        conn.commit()
        return 1

    def update_user_last_name(self,user_id, last_name):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        cursor.execute("UPDATE User SET l_name=? WHERE id=?", (last_name, user_id))
        conn.commit()
        return 1

    def update_user_password(self,user_id, old_pass, new_pass):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        real_old_pass = cursor.execute("SELECT pass FROM Log_in WHERE user_id=?", (user_id,)).fetchone()
        if real_old_pass and old_pass == real_old_pass[0]:
            if len(new_pass) >= 9:
                cursor.execute("UPDATE Log_in SET pass=? WHERE user_id=?", (new_pass, user_id))
                conn.commit()
                return 1
        return 0

    def Subscription_info(self,ID):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        self.ID=ID
        data_dic=[]
        info_of_book=cursor.execute("SELECT books_id, s_date, e_date FROM Subscription WHERE user_id=?",(self.ID,)).fetchall()
        if info_of_book:
            book_id=[]
            start_book=[]
            end_book=[]
            for book in info_of_book:
                book_id.append(book[0])
                start_book.append(book[1])
                end_book.append(book[2])
            name_of_book=[]
            name=[]

            print("\n")
            for x in range(len(book_id)):
                name_of_book=cursor.execute("SELECT name FROM Books WHERE id=?",(book_id[x],)).fetchall()
                name.append(name_of_book[0][0])
            for x in range(len(book_id)):
                data_dic.append((name[x],book_id[x],start_book[x],end_book[x]))

            return data_dic
        else:
            print("You are not borrowing a book ")
            return data_dic

    def create_account(self, __user_name, __password, __email, __phone, __f_name, __l_name, type_user):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        # ID جديد
        max_id = cursor.execute("SELECT MAX(id) FROM User").fetchone()[0]
        id = (max_id or 0) + 1

        # التحقق من اسم المستخدم
        if not (len(__user_name) >= 9 and any(x in string.digits for x in __user_name)):
            return {"status": False, "field": "username", "message": "Username must contain letters, numbers, and be at least 9 characters long."}

        check = cursor.execute("SELECT user_name FROM Log_in WHERE user_name=?", (__user_name,)).fetchone()
        if check:
            return {"status": False, "field": "username", "message": "Invalid username format or length."}

        # التحقق من الباسورد
        if len(__password) <= 9:
            return {"status": False, "field": "password", "message": "Password must be longer than 9 characters."}



        # التحقق من الإيميل
        check = cursor.execute("SELECT email FROM User WHERE email=?", (__email,)).fetchone()
        if check:
            return {"status": False, "field": "email", "message": "Invalid email format or already in use."}

        if not gmail_obj.is_valid_gmail(__email):
            return {"status": False, "field": "email", "message": "Email must be a valid Gmail address."}


        # إدخال البيانات في الجدول
        today = datetime.today().strftime("%d/%m/%Y")
        user_type = "user"

        cursor.execute("""
            INSERT INTO User (phone, email, date, type_user, id, f_name, l_name, user_type, photo_url )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (__phone, __email, today, type_user, id, __f_name, __l_name, user_type, "/static/photo_user/defulte_photo.jpg"))

        cursor.execute("""
            INSERT INTO Log_in (pass, user_name, user_id)
            VALUES (?, ?, ?)
        """, (__password, __user_name, id))

        

        conn.commit()

        return {
            "status": True,
            "message": "Account created successfully.",
            "data": {
                "id": id,
                "username": __user_name,
                "first_name": __f_name,
                "last_name": __l_name,
                "type_user": type_user,
                "email": __email,
                "phone": __phone
            }
        }
    
    def check_info_dub_send(self, email=None, phone=None):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        # تأكد إن المستخدم دخل حاجة على الأقل
        if not email and not phone:
            return "You must enter email or phone"

        # لو دخل ايميل
        if email:
            email_DB = cursor.execute("SELECT email FROM User WHERE email=?", (email,)).fetchall()
            if email_DB != []:
                return "Email is already exist"

        # لو دخل رقم تليفون
        if phone:
            phone_DB = cursor.execute("SELECT phone FROM User WHERE phone=?", (phone,)).fetchall()
            if phone_DB != []:
                return "Phone is already exist"

        # لو وصل هنا يبقى المدخلات كلها valid
        if email:  # لو فيه ايميل ابعتله كود التفعيل
            gmail_obj.send_message_random_code(email)

        return 1
        

    def check_ver_code(self,code):
        if int(code)==gmail_obj.get_random_var():
            return 1
        else:
            return 0


    def Log_in(self,user_name,password):
        try:
            db=Data_Base().check_login(user_name,password)
            ID=db[0]
            db2 = Data_Base()
            conn = sqlite3.connect(db2._get_url())
            cursor = conn.cursor()
            match db[1]:
                case 1:# role 
                    Names=cursor.execute("SELECT f_name, l_name FROM User WHERE id=?",(ID,)).fetchall()
                    print("\n")
                    print(f"Welcome\n{Names[0][0]} {Names[0][1]}")
                    return ID,1
                case 2:
                    Names = cursor.execute("SELECT f_name, l_name FROM Librarian WHERE id=?", (ID,)).fetchall()
                    print("\n")
                    print(f"Welcome\n{Names[0][0]} {Names[0][1]}")
                    return ID,2
                case 3:
                    Names = cursor.execute("SELECT f_name, l_name FROM Manager WHERE id=?", (ID,)).fetchall()
                    print("\n")
                    print(f"Welcome\n{Names[0][0]} {Names[0][1]}")
                    return ID,3
                case _:
                    print("False pass")
                    return 0
        except :
            print("try again")
            return 0



    def get_photo_url(self, ID,state):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        if(state==1):
            print(cursor.execute("SELECT photo_url FROM User WHERE id=?",(ID,)).fetchall())
            return cursor.execute("SELECT photo_url FROM User WHERE id=?",(ID,)).fetchall()
        elif(state==2):
            return cursor.execute("SELECT photo_url FROM Librarian WHERE id=?",(ID,)).fetchall()
        elif(state==3):
            return [('/static/photo_user/defulte_photo.jpg',)]
        else:
            return 0
    


    def update_photo_url(self,id,path,state):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        if(state==1):
            cursor.execute("UPDATE User SET photo_url = ? WHERE id = ?",(path,id)).fetchall()
            conn.commit()
            return 
        elif(state==2):
            return cursor.execute("UPDATE Librarian SET photo_url = ? WHERE id = ?",(path,id)).fetchall()
        elif(state==3):
            return cursor.execute("UPDATE User SET photo_url = ? WHERE id = ?",(path,id)).fetchall()
        else:
            return 0


    def user_info(self,state,ID):
        db = Data_Base()
        conn=sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        if(state==1):#user
            data=cursor.execute("SELECT * FROM User WHERE id=?",(ID,)).fetchall()
            if data:
                data_dic={}
                data_dic["phone"]=data[0][0]
                data_dic["email"]=data[0][1]
                data_dic["date"]=data[0][2]
                data_dic["type_user"]=data[0][3]
                data_dic["id"]=data[0][4]
                data_dic["first_name"]=data[0][6]
                data_dic["l_name"]=data[0][7]
                data_dic["photo_url"]=data[0][8]
                print(data_dic)
                return data_dic
            else:
                return 0
        elif(state==2):#librarain
            data=cursor.execute("SELECT * FROM Librarian WHERE id=?",(ID,)).fetchall()
            if data:
                data_dic={}
                data_dic["phone"]=data[0][0]
                data_dic["first_day_date"]=data[0][1]
                data_dic["type_user"]=data[0][8]
                data_dic["id"]=data[0][5]
                data_dic["f_name"]=data[0][3]
                data_dic["l_name"]=data[0][4]
                data_dic["photo_url"]=data[0][9]
                print(data_dic)
                return data_dic
            else:
                return 0
        elif(state==3):#manager
            pass
        else:
            return 0

User().user_info(2,931230239)