from Gmail_Sender import *
from Data_base import Data_Base
import sqlite3
from Gmail_Sender import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Manager(Data_Base):

    def search(self,phone,librarian=None,ID=None):
        db=Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()
            if(librarian==None and ID==None):
                search=cursor.execute("SELECT phone FROM User WHERE phone=?",(phone,)).fetchall()
                if search:
                    return 0
                else:
                    return 1
            elif(ID==None):
                search = cursor.execute("SELECT phone FROM Librarian WHERE phone=?", (phone,)).fetchall()
                if search:
                    return 0
                else:
                    return 1
            elif(phone==None and librarian==None):#search by ID
                search = cursor.execute("SELECT id FROM User WHERE id=?", (ID,)).fetchall()
                if search:
                    return 1
                else:
                    return 0
            elif (phone == None):  # search by ID
                search = cursor.execute("SELECT id FROM librarian WHERE id=?", (ID,)).fetchall()
                if search:
                    return 1
                else:
                    return 0

    import sqlite3
    from datetime import datetime

    def add_new(self, chouice, user_data):
        if chouice == 1:
            return self._add_new_user(user_data)
        elif chouice == 2:
            return self._add_new_librarian(user_data)
        else:
            return 0

    def _add_new_user(self, user_data):
        db = Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()

            __Phone = user_data['phone']
            if Manager().search(__Phone):
                __email = user_data['email']
                if is_valid_gmail(__email):
                    send_message(__email)
                    ran = user_data['verification_code']
                    if ran == random_var():
                        today = datetime.today()
                        s_date = today.strftime("%d/%m/%Y")
                        type_user = user_data['type_user']
                        if type_user.lower() in ["student", "searcher"]:
                            data = cursor.execute("SELECT MAX(id) FROM User").fetchall()
                            new_id = data[0][0] + 1
                            __f_name = user_data['f_name']
                            __l_name = user_data['l_name']
                            add = user_data['address']
                            user_type = "user"
                            cursor.execute(
                                "INSERT INTO User (phone, email, date, type_user, id, add, f_name, l_name, user_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (__Phone, __email, s_date, type_user, new_id, add, __f_name, __l_name, user_type)
                            ).fetchall()
                            conn.commit()
                            return 1
        return 0

    def _add_new_librarian(self, librarian_data):
        db = Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()

            __Phone = librarian_data['phone']
            if Manager().search(__Phone, 1):
                today = datetime.today()
                s_date = today.strftime("%d/%m/%Y")

                __salary = librarian_data['salary']
                __f_name = librarian_data['f_name']
                __l_name = librarian_data['l_name']
                __username = librarian_data['username']
                __password = librarian_data['password']
                manager_id = librarian_data['manager_id']
                library_id = librarian_data['library_id']
                user_type = "librarian"
                photo_url="/static/photo_user/defulte_photo.jpg"

                data = cursor.execute("SELECT MAX(id) FROM Librarian").fetchone()
                new_id = (data[0] if data[0] else 0) + 1

                cursor.execute("""
                    INSERT INTO Librarian (phone, first_day_date, salary, f_name, l_name, id, manager_id, library_id, user_type,photo_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (__Phone, s_date, __salary, __f_name, __l_name, new_id, manager_id, library_id, user_type, photo_url))

                cursor.execute("""
                    INSERT INTO Log_in (pass, user_name, librarian_id)
                    VALUES (?, ?, ?)
                """, (__password, __username,new_id))

                conn.commit()

            conn.commit()
            return {"status": True, "message": "Librarian added successfully"}
        return {"status": False, "message": "Phone already exists"}

    def remove(self, choice, ID):
        db = Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()

            if choice == 1:
                if Manager().search(None, None, ID):
                    cursor.execute("DELETE FROM User WHERE id = ?", (ID,)).fetchall()
                    conn.commit()
                    return 1
                else:
                    return 0

            elif choice == 2:
                if Manager().search(None, 1, ID):
                    cursor.execute("DELETE FROM Librarian WHERE id = ?", (ID,)).fetchall()
                    conn.commit()
                    return 1
                else:
                    return 0
            else:
                return 0

    def check_financial(self):
        db = Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()
            data=cursor.execute("SELECT user_id, payment FROM Subscription ORDER BY payment DESC").fetchall()
            user_id=[];payment=[];data_dic=[]
            for x in data:
                user_id.append(x[0])
                payment.append(x[1])
            for x in range(len(user_id)):
                data_dic.append((user_id[x],payment[x]))
            return data_dic

    def over_all_book(self):
        db = Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()
            data_dic=[]
            data=cursor.execute("SELECT * FROM Books").fetchall()
            name=[];id=[];user_id=[];author=[];type=[];price=[];branch_id=[];info=[]
            for x in data:
                name.append(x[0])
                id.append(x[1])
                user_id.append(x[2])
                author.append(x[3])
                type.append(x[4])
                price.append(x[5])
                branch_id.append(x[6])
                info.append(x[7])
            print("Name\tID\tUser_id\tAuthor\tType\tPrice\tBranch_id\tInfo")
            for x in range(len(name)):
                print(name[x],"\t",id[x],"\t",user_id[x],"\t",author[x],"\t",type[x],"\t",price[x],"\t",branch_id[x])
                data_dic.append((name[x],id[x],user_id[x],author[x],type[x],price[x],branch_id[x]))
            return data_dic
    
    def managers_ids(self):
        db = Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()
            ids=cursor.execute("SELECT id FROM Manager").fetchall()
            return ids

    def library_num(self):
        db = Data_Base()
        with sqlite3.connect(db._get_url()) as conn:
            cursor = conn.cursor()
            ids=cursor.execute("SELECT branch_id FROM Library").fetchall()
            return ids
