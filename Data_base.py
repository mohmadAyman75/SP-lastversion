import sqlite3
import re



class Data_Base:
    def __init__(self):
        self.ID=0
        self.Name=""
        self.__user_Name=""
        self.__pass=0
        import os

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "library_DB.db")

        self.__url=db_path



    def get_recent_book(self):   #abstract method #worked
        pass



    def check_ID_in_table(self):  #worked in librarian,..
        pass



    """
    
    def get_info_book(self,__Book_ID):
        conn = sqlite3.connect(self.__url)
        cursor = conn.cursor()
        db=Data_Base()
        db.check_ID_in_table()



        self.ID=__Book_ID

        def db():
            data=cursor.execute("SELECT info FROM Books WHERE id = ?",(self.ID,)).fetchall()
            if data:
                return 1
            else:
                print("False ID try again\n")
                return 0

        if db():
            data_dic=[]
            Name_of_book=cursor.execute("SELECT name FROM books WHERE id = ?",(self.ID,)).fetchall()
            cursor.execute("SELECT info FROM Books WHERE id=?",(self.ID,))
            data=cursor.fetchall()
            print(f"Name:{Name_of_book[0]}\ninforamtion:{data[0]}")
            for x in Name_of_book:
                data_dic.append((Name_of_book[0],data[0]))
            return data_dic     """



    def _get_url(self):
        return self.__url
    
    def _get_url2(self,id):
        conn = sqlite3.connect(self.__url)
        cursor = conn.cursor()
        data_dic=cursor.execute("SELECT book_url FROM Books WHERE id = ?", (id,)).fetchall()
        print(data_dic)
        return data_dic
        

    def check_login(self,__user_name,__password):
        # 1=user , 2=librarian , 3=manager , 0=False
        self.__user_Name = __user_name
        self.__pass = __password

        conn = sqlite3.connect(self.__url)
        cursor = conn.cursor()

        result = cursor.execute("""
            SELECT user_id, librarian_id, manager_id 
            FROM Log_in 
            WHERE user_name = ? AND pass = ?
        """, (self.__user_Name, self.__pass)).fetchone()
        conn.commit()
        conn.close()

        if result:
            user_id, librarian_id, manager_id = result

            if user_id is not None:
                self.ID = user_id
                return self.ID, 1
            elif librarian_id is not None:
                self.ID = librarian_id
                return self.ID, 2
            elif manager_id is not None:
                self.ID = manager_id
                return self.ID, 3


        self.ID = None
        return self.ID, 0



    def search(self): #Not worked
        pass


    def add_new(self):#احتمال امسحها (الفكره اني لما اجي اعمل فانكشن الارجيومنت هيكونوا 8 تقريبا والكلام دا مش منطقي)
        #stuff or user
        pass

    def remove(self):
        pass

    def get_photo_url(self,ID):
        pass


    def Log_in(self ,user_name,password):
        pass

    def user_info(self,state,ID):
        pass


    def remove_l_u(self, librarian_id=None, user_id=None):
            conn = sqlite3.connect(self.__url)
            cursor = conn.cursor()
            
            if librarian_id:
                cursor.execute("DELETE FROM Log_in WHERE librarian_id=?", (librarian_id,))
                cursor.execute("DELETE FROM Librarian WHERE id=?", (librarian_id,))
                
            if user_id:
                cursor.execute("DELETE FROM Log_in WHERE user_id=?", (user_id,))
                cursor.execute("DELETE FROM User WHERE id=?", (user_id,))
                
            conn.commit()
            cursor.close()
            conn.close()


    
    def get_user_librarian_data(self, user_id=None, librarian_id=None):
        conn = sqlite3.connect(self.__url)
        cursor = conn.cursor()
        
        result = []
        
        if user_id:
            cursor.execute("SELECT id, f_name, l_name FROM User")
            user_data = cursor.fetchall()
            for data in user_data:
                result.append((data[0], data[1], data[2], "user"))
        
        if librarian_id:
            cursor.execute("SELECT id, f_name, l_name FROM Librarian")
            librarian_data = cursor.fetchall()
            for data in librarian_data:
                result.append((data[0], data[1], data[2], "librarian"))
        
        cursor.close()
        conn.close()
        
        return result

    def get_user_type(self, user_id):
        # الاتصال بقاعدة البيانات للتحقق من نوع المستخدم
        conn = sqlite3.connect(self.__url)
        cursor = conn.cursor()
        
        # تحقق أولاً إذا كان الـ user_id في جدول Librarian
        cursor.execute("SELECT id FROM Librarian WHERE id=?", (user_id,))
        librarian = cursor.fetchone()
        
        # إذا وجدنا الـ user_id في جدول Librarian، فهو "أمين مكتبة"
        if librarian:
            return "librarian"
        
        # تحقق من جدول User إذا لم يكن في جدول Librarian
        cursor.execute("SELECT id FROM User WHERE id=?", (user_id,))
        user = cursor.fetchone()
        
        # إذا وجدنا الـ user_id في جدول User، فهو "مستخدم"
        if user:
            return "user"
        
        # إذا لم يتم العثور عليه في أي من الجداول
        return None