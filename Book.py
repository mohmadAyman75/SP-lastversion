from Data_base import Data_Base
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Book(Data_Base):
    def __init__(self):
        self.Book_Name=""
        self.Author=""

    def check_ID_in_table(self,__User_id,__books_id=None):
        if __books_id==None:
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            test=cursor.execute("SELECT user_id FROM Subscription WHERE user_id=?", (__User_id,)).fetchall()
            if test:
                conn.commit()
                conn.close()
                return 1
            else:
                conn.commit()
                conn.close()
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


    def search_book(self):
        self.Book_Name=input("Enter book name:")
        db_search = Data_Base()
        db_search.search()
        db=Data_Base()
        def db_search():
            conn=sqlite3.connect(db._get_url())
            Book_Name=conn.cursor().execute("SELECT name FROM Books WHERE name=?",(self.Book_Name.lower(),)).fetchall()
            if Book_Name:
                print(f"is founded: {Book_Name[0]}")
                data = conn.cursor().execute("SELECT name , id, author, price, branch_id, info FROM Books WHERE name=?",(self.Book_Name.lower(),)).fetchall()
                print("name\tid\tauthor\tprice\tbranch id\tinfo")
                print(data[0])
                conn.commit()
                conn.close()
            else:
                print(f"this Book unavailable")
                conn.commit()
                conn.close()
        db_search()

    def all_book(self):
        db_search=Data_Base()
        db_search.search()
        db=Data_Base()

        data_dic=[]
        def db_search():
            conn=sqlite3.connect(db._get_url())

            data=conn.cursor().execute("SELECT name, author, price, branch_id, info, photo_url, id, more_info, book_url FROM Books").fetchall()

            data_dic.append(data)
            conn.commit()
            conn.close()
            return data_dic
        return db_search()

    def Availalbe_books(self):
        pass


    def borrowed_book(self,__User_id ):
        try:
            __Librarian_id = 00
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            BB=Book()
            check_itis_user = cursor.execute("SELECT id FROM User WHERE id=?", (__User_id,)).fetchall()
            if (check_itis_user):
                __books_id = int(input("Enter book id:"))
                if  BB.check_ID_in_table(__User_id, __books_id)== 0:
                    monthe_number = int(input("Enter month number(1,2,3):"))
                    today = datetime.today()
                    s_date = today.strftime("%d/%m/%Y")
                    date_obj = datetime.strptime(s_date, "%d/%m/%Y")
                    __payment = 125
                    match monthe_number:
                        case 1:
                            new_date = date_obj + relativedelta(months=1)
                            new_date_str = new_date.strftime("%d/%m/%Y")
                            print("the Subscription will end at :", new_date_str)
                            print("started in:", s_date)
                            test = cursor.execute(
                                "INSERT INTO Subscription (user_id, books_id, librarian_id, s_date, e_date, payment)VALUES (?, ?, ?, ?, ?, ?)",
                                (__User_id, __books_id, __Librarian_id, s_date, new_date_str, __payment,)).fetchall()
                            conn.commit()
                            return 1
                        case 2:
                            new_date = date_obj + relativedelta(months=2)
                            new_date_str = new_date.strftime("%d/%m/%Y")
                            print("the Subscription will end at :", new_date_str)
                            print("started in:", s_date)
                            test = cursor.execute(
                                "INSERT INTO Subscription (user_id, books_id, librarian_id, s_date, e_date, payment)VALUES (?, ?, ?, ?, ?, ?)",
                                (__User_id, __books_id, __Librarian_id, s_date, new_date_str, __payment,)).fetchall()
                            conn.commit()
                            return 1
                        case 3:
                            new_date = date_obj + relativedelta(months=3)
                            new_date_str = new_date.strftime("%d/%m/%Y")
                            print("the Subscription will end at :", new_date_str)
                            print("started in:", s_date)
                            test = cursor.execute(
                                "INSERT INTO Subscription (user_id, books_id, librarian_id, s_date, e_date, payment)VALUES (?, ?, ?, ?, ?, ?)",
                                (__User_id, __books_id, __Librarian_id, s_date, new_date_str, __payment,)).fetchall()
                            return 1
                        case _:
                            print("you can only update for 1 or 2 or 3 months")
                            return 0
                else:
                    print("this book already is taken..")
            else:
                print("ID is wrong..")
        except Exception as e:
            print(e)





    def get_info_book(self):
        db=Data_Base().get_info_book()
        db




    def Log_in(self):
        pass

    def get_user_rating(self, user_id, book_id):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        cursor.execute("""
            SELECT rating FROM Rating_Value 
            WHERE user_id = ? AND book_id = ?
        """, (user_id, book_id))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None


    def insert_rating(self, user_id, book_id, rating_value):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Rating_Value (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (book_id) REFERENCES Books(id),
                UNIQUE(user_id, book_id)
            )
        ''')

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id=cursor.execute("SELECT MAX(id) FROM Rating_Value").fetchall()

        new_id=id[0][0]+1
        # إدخال أو تحديث التقييم
        cursor.execute('''
            INSERT INTO Rating_Value (user_id, book_id, rating, date, id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, book_id, rating_value, current_date, new_id,))

        conn.commit()
        conn.close()

    def get_top_book(self):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        
        # استعلام مبسط وأكثر كفاءة
        top_books = cursor.execute("""
            SELECT 
                book_id,
                COUNT(rating) AS rating_count,
                AVG(rating) AS avg_rating
            FROM Rating_Value
            GROUP BY book_id
            ORDER BY avg_rating DESC, rating_count DESC
        """).fetchall()
        
        if not top_books:
            conn.close()
            return []
        
        # الحفاظ على ترتيب التصنيف
        book_ids = [str(row[0]) for row in top_books]
        id_to_rank = {book_id: idx for idx, book_id in enumerate(book_ids)}
        
        placeholders = ",".join(book_ids)
        books_data = cursor.execute(f"""
            SELECT 
                name, author, price, branch_id, 
                info, photo_url, id, more_info, book_url
            FROM Books
            WHERE id IN ({placeholders})
        """).fetchall()
        
        conn.close()
        
        # إعادة الترتيب حسب التصنيف الأصلي
        books_data.sort(key=lambda x: id_to_rank[str(x[6])])
        
        return [{
            "name_book": row[0],
            "author": row[1].strip() if row[1] else None,
            "price": row[2],
            "branch_id": row[3],
            "info": row[4],
            "photo_url": row[5],
            "id": row[6],
            "more_info": row[7],
            "book_url": row[8]
        } for row in books_data]



    def add_my_books(self,userid,bookid,status):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        date=datetime.now().strftime("%d/%m/%Y")
        if status==1:#favorite
            insert_data=cursor.execute("INSERT INTO 'My Books' (`book id`, `user id`, date, `favorite book`) VALUES(?, ?, ?, ?)", (bookid, userid, date, 1))
            conn.commit()
            return 1
        elif status==2:#downloaded
            insert_data = cursor.execute("INSERT INTO `My Books` (`book id`, `user id`, date, `downloaded book`) VALUES (?, ?, ?, ?)", (bookid, userid, date, 1))
            conn.commit()
            conn.close()
            return 1
        else:
            return 0
        
    def get_my_books(self,userid,status):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        date=datetime.now().strftime("%d/%m/%Y")
        if status==1:#favorite
            output_data=cursor.execute("SELECT `book id` FROM 'My Books' WHERE `user id` = ? AND `favorite book` = 1", (userid,)).fetchall()
            data_list=[]
            for x in output_data:
                data_list.append(*x)
            conn.commit()
            conn.close()
            return data_list
        elif status==2:#downloaded
            output_data=cursor.execute("SELECT `book id` FROM 'My Books' WHERE `user id` = ? AND `downloaded book` = 1", (userid,)).fetchall()
            data_list=[]
            for x in output_data:
                data_list.append(*x)
            conn.commit()
            conn.close()
            return data_list
        else:
            return 0
        
    def get_custom_book(self,list_books):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        result = []
        
        for i in list_books:
            Books_data = cursor.execute("""
                SELECT name, author, price, branch_id, info, photo_url, id, more_info, book_url 
                FROM Books 
                WHERE id=?
            """, (i,)).fetchall()
            
            result.extend([
                {
                    "name_book": x[0], 
                    "author": x[1].strip(), 
                    "price": x[2], 
                    "branch_id": x[3], 
                    "info": x[4], 
                    "photo_url": x[5], 
                    "id": x[6], 
                    "more_info": x[7], 
                    "book_url": x[8]
                } 
                for x in Books_data
            ])
        conn.commit()
        conn.close()
        return result

    def update_book(self,book_id,data_dic={}):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()

        update_operation=cursor.execute("UPDATE Books SET name=?, author=?, price=?, more_info=? WHERE id=?",(data_dic['name_book'],data_dic['author'],data_dic['price'],data_dic['more_info'],book_id))
        conn.commit()
        updated_rows = cursor.rowcount

        conn.close()
        return 1

    def DashBoard_data(self,status=0):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        if status==0:
            query = """SELECT "book id", COUNT(*) AS downloads FROM "My Books" WHERE "downloaded book" = 1 GROUP BY "book id" ORDER BY downloads DESC; """
            data=cursor.execute(query).fetchall()
            id=[]
            numer_of_downloads=[]
            names_of_books=[]
            for i in data:
                id.append(i[0])
                numer_of_downloads.append(i[1])
            for x in id:
                names_books=cursor.execute("SELECT name FROM Books WHERE  id =?",(x,)).fetchall()
                names_of_books.append(names_books[0][0])

            data_dic={"id":id,"num_down":numer_of_downloads,"names":names_of_books}
            return data_dic
        elif status==4:
            num_user=cursor.execute("SELECT id FROM User").fetchall()
            num_book=cursor.execute("SELECT id FROM Books").fetchall()
            num_librarian=cursor.execute("SELECT id FROM Librarian").fetchall()
            rating_book=cursor.execute("SELECT rating FROM Rating_Value").fetchall()
            total = sum(x[0] for x in rating_book)

            return len(num_user ),len(num_book),len(num_librarian),((total/len(rating_book))/5)*100
        if status == 1:
            # هات الـ id + الافريدج بتاع الريتنج
            ratings = cursor.execute("""
                SELECT 
                    book_id, 
                    MIN(AVG(rating), 5) as avg_rating
                FROM Rating_Value
                GROUP BY book_id
            """).fetchall()

            results = []
            for book_id, avg_rating in ratings:
                # هات اسم الكتاب من الـ Books
                book_name = cursor.execute("SELECT name FROM Books WHERE id = ?", (book_id,)).fetchone()

                if book_name:
                    results.append((book_name[0], avg_rating))

            return results


        elif status == 2:
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()

            data = cursor.execute("SELECT * FROM User").fetchall()


            if data:
                data_list = []
                for data1 in data:
                    user_tuple = (
                        data1[4],
                        data1[6],
                        data1[7],

                        data1[1], 
                        data1[2]
                    )
                    data_list.append(user_tuple)

                return tuple(data_list)


        elif status ==3:
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()

            data = cursor.execute("SELECT * FROM Librarian").fetchall()


            if data:
                data_list = []
                for data1 in data:
                    user_tuple = (
                        data1[0],
                        data1[1],
                        data1[2],
                        data1[3],
                        data1[4],
                        data1[5], 
                        data1[6],
                        data1[7]
                    )
                    data_list.append(user_tuple)

                return tuple(data_list)


