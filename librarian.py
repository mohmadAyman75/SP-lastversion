from Gmail_Sender import *
from Data_base import Data_Base
import sqlite3
from Book import Book
from datetime import datetime
from dateutil.relativedelta import relativedelta
from user import User

class Librarian(Book):

    def get_recent_book(self):
        pass


    def check_ID_in_table(self,__User_id,__books_id=None):
        if __books_id==None:
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            test=cursor.execute("SELECT user_id FROM Subscription WHERE user_id=?", (__User_id,)).fetchall()
            if test:
                return 1
            else:
                return 0
        else:
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            test = cursor.execute("SELECT books_id FROM Subscription WHERE books_id=?", (__books_id,)).fetchall()
            if test:
                return 1
            else:
                return 0


    def add_new_book(self, dic_data=dict):
        try:
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()

            # توليد ID جديد تلقائيًا
            max_id = cursor.execute("SELECT MAX(id) FROM Books").fetchone()
            new_id = (max_id[0] if max_id[0] is not None else 0) + 1

            # قراءة البيانات من القاموس
            name = dic_data.get("name")
            user_id = dic_data.get("user_id")
            author = dic_data.get("author")
            type_book = dic_data.get("type")
            price = dic_data.get("price")
            branch_id = dic_data.get("branch_id")
            info = dic_data.get("info")
            photo_url = dic_data.get("photo_url")
            more_info = dic_data.get("more_info")
            book_url = dic_data.get("book_url")

            # تنفيذ أمر الإدخال
            cursor.execute("""
                INSERT INTO Books 
                (name, id, user_id, author, type, price, branch_id, info, photo_url, more_info, book_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, new_id, user_id, author, type_book, price, branch_id,
                info, photo_url, more_info, book_url
            ))

            conn.commit()
            return 1

        except Exception as e:
            print("error", e)
            return 0


    def update_sub(self,__Librarian_id,user_id,book_id,payment,months):
        try:
            db = Data_Base()
            lb=Librarian()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            __User_id=user_id
            if lb.check_id_in_table(__User_id):
                __books_id=book_id
                if lb.check_id_in_table(__User_id,__books_id):
                    __payment=payment
                    monthe_number=months,"""int(input("Enter month number(1,2,3):"))"""
                    today = datetime.today()
                    s_date = today.strftime("%d/%m/%Y")
                    date_obj = datetime.strptime(s_date, "%d/%m/%Y")
                    match monthe_number:
                        case 1:
                                new_date = date_obj + relativedelta(months=1)
                                new_date_str = new_date.strftime("%d/%m/%Y")
                                """print("the Subscription will end at :",new_date_str)
                                print("started in:",s_date)"""
                                test=cursor.execute("UPDATE Subscription set user_id=?, books_id=?, librarian_id=?, s_date=?, e_date=?, payment=? WHERE user_id=? AND books_id=?",(__User_id,__books_id,__Librarian_id,s_date,new_date_str,__payment,__User_id,__books_id)).fetchall()
                                conn.commit()
                                return 1
                        case 2:
                                new_date = date_obj + relativedelta(months=2)
                                new_date_str = new_date.strftime("%d/%m/%Y")
                                """print("the Subscription will end at :", new_date_str)
                                print("started in:", s_date)"""
                                test = cursor.execute(
                                    "UPDATE Subscription set user_id=?, books_id=?, librarian_id=?, s_date=?, e_date=?, payment=? WHERE user_id=? AND books_id=?",
                                    (__User_id, __books_id, __Librarian_id, s_date, new_date_str, __payment,
                                     __User_id, __User_id)).fetchall()
                                conn.commit()
                                return 1
                        case 3:
                                new_date = date_obj + relativedelta(months=3)
                                new_date_str = new_date.strftime("%d/%m/%Y")
                                """print("the Subscription will end at :", new_date_str)
                                print("started in:", s_date)"""
                                test = cursor.execute(
                                    "UPDATE Subscription set user_id=?, books_id=?, librarian_id=?, s_date=?, e_date=?, payment=? WHERE user_id=? AND books_id=?",
                                    (__User_id, __books_id, __Librarian_id, s_date, new_date_str, __payment,
                                     __User_id, __books_id)).fetchall()
                                conn.commit()
                                return 1
                        case _:
                                """print("you can only update for 1 or 2 or 3 months")"""
                                return 0

            else:
                """print("this account don`t  have any book to update date..")"""
                return 0
        except:
                """print("try again")"""
                return 0


    def lend_book(self,__Librarian_id,user_id,book_id,payment,months):
        try:
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            lb=Librarian()
            __User_id=user_id
            check_itis_user=cursor.execute("SELECT id FROM User WHERE id=?",(__User_id,)).fetchall()
            if (check_itis_user):
                __books_id=book_id
                check_book_id=cursor.execute("SELECT books_id FROM Subscription WHERE books_id=?",(__books_id,)).fetchall()
                print(check_book_id)
                if lb.check_id_in_table(__User_id,__books_id)==0:
                    __payment=payment
                    monthe_number=months,"""int(input("Enter month number(1,2,3):"))"""
                    today = datetime.today()
                    s_date = today.strftime("%d/%m/%Y")
                    date_obj = datetime.strptime(s_date, "%d/%m/%Y")
                    match monthe_number:
                        case 1:
                                new_date = date_obj + relativedelta(months=1)
                                new_date_str = new_date.strftime("%d/%m/%Y")
                                """print("the Subscription will end at :",new_date_str)
                                print("started in:",s_date)"""
                                test=cursor.execute("INSERT INTO Subscription (user_id, books_id, librarian_id, s_date, e_date, payment)VALUES (?, ?, ?, ?, ?, ?)",(__User_id,__books_id,__Librarian_id,s_date,new_date_str,__payment,)).fetchall()
                                conn.commit()
                                return 1
                        case 2:
                                new_date = date_obj + relativedelta(months=2)
                                new_date_str = new_date.strftime("%d/%m/%Y")
                                """print("the Subscription will end at :", new_date_str)
                                print("started in:", s_date)"""
                                test=cursor.execute("INSERT INTO Subscription (user_id, books_id, librarian_id, s_date, e_date, payment)VALUES (?, ?, ?, ?, ?, ?)",(__User_id,__books_id,__Librarian_id,s_date,new_date_str,__payment,)).fetchall()
                                conn.commit()
                                return 1
                        case 3:
                                new_date = date_obj + relativedelta(months=3)
                                new_date_str = new_date.strftime("%d/%m/%Y")
                                """print("the Subscription will end at :", new_date_str)
                                print("started in:", s_date)"""
                                test=cursor.execute("INSERT INTO Subscription (user_id, books_id, librarian_id, s_date, e_date, payment)VALUES (?, ?, ?, ?, ?, ?)",(__User_id,__books_id,__Librarian_id,s_date,new_date_str,__payment,)).fetchall()
                                return 1
                        case _:
                                """print("you can only update for 1 or 2 or 3 months")"""
                                return 0
                else:
                    """print("this book already is taken..")"""
                    return 0
        except:
            """print("error input")"""
            return 0


    def manage_user(self,chouice,user_id,new_phone=None,new_email=None,var_code=None,fir_name=None,las_name=None,old_pass=None,new_pass=None):
        user_id=int(input("Enter user ID:"))
        user=User().update_info(user_id)
        match chouice:
            case 1:
                    User.update_user_phone(user_id,new_phone)
                    return 1
            case 2:
                    User.update_user_email(user_id,new_email,var_code)
                    return 1
            case 3:
                    User.update_user_first_name(user_id,fir_name)
                    return 1
            case 4:
                    User.update_user_last_name(user_id,las_name)
                    return 1
            case 5:
                    User.update_user_password(user_id,old_pass,new_pass)
                    return 1
            case _:
                print("Flase")
                return 0


    def process_return(self,_user_id,_book_id):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        user_id=_user_id
        book_id=_book_id
        cursor.execute("DELETE FROM Subscription WHERE user_id=? AND books_id=?",(user_id,book_id,))
        conn.commit()
        """print("operation success")"""
        return 1

    def manipulate_copies(self):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        books=cursor.execute("SELECT name, COUNT(*) as count FROM Books GROUP BY name HAVING count > 1").fetchall()
        Names=[];numbers=[];data_dic=[]
        for x in books:
            Names.append(x[0])
            numbers.append(x[1])
        for x in range(len(Names)):
            """print("Name of book:",Names[x],"Number:",numbers[x])"""
            data_dic.append((Names[x],numbers[x]))
        return data_dic


