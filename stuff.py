from Data_base import Data_Base
from datetime import datetime, date
import sqlite3
class Stuff:
    db=Data_Base()

    def _generate_reports(self):
        print(f"""==========================================
Alexandria Library - Daily Report
Branch: [Alexandria branch]
Date: [{date.today()}]
==========================================""")
        def display_daily_rep():
            print("_"*20)
            print("1-DAILY LOANS")
            #display recent borrowed book
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            cursor.execute("SELECT s_date FROM Subscription")
            rows = cursor.fetchall()
            x=0;total_payment=0
            for row in rows:
                s_date_str = row[0]
                s_date_obj = datetime.strptime(s_date_str, "%d/%m/%Y").date()
                today = date.today()
                delta = today - s_date_obj
                if delta.days<=2:
                    info=cursor.execute("SELECT * FROM Subscription WHERE s_date=?",(s_date_str,)).fetchall()
                    total_payment=total_payment+info[x][5]
                    print("[user_id] [books_id] [librarian_id] [S-date] [e_date] [payment]")
                    print(info[x],"\n")
                    x+=1
            print(f"the total payment today is: {total_payment}")
        def library_summary():
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            numer_book=cursor.execute("SELECT COUNT(*) FROM Books").fetchall()#
            numer_avil_book=cursor.execute("SELECT COUNT(*) FROM Books WHERE user_id IS NULL").fetchall()
            number_not_avil_book=cursor.execute("SELECT COUNT(*) FROM Books WHERE user_id IS NOT NULL").fetchall()
            print("_"*25)
            print("2- INVENTORY SUMMARY")
            print("- Total items:",numer_book[0][0])
            print("- Available items:",numer_avil_book[0][0])
            print("- Checked out:",number_not_avil_book[0][0])


        def top_requested():
            db = Data_Base()
            conn = sqlite3.connect(db._get_url())
            cursor = conn.cursor()
            info=cursor.execute("""
                SELECT type, COUNT(*) as count
                FROM Books
                GROUP BY type
                ORDER BY count DESC
                """).fetchall()
            print("_"*25)
            print("Top requested items:")

            for x in range(len(info)):
                print(info[x])


        top_requested()
        display_daily_rep()
        library_summary()



    def update_info(self):
        pass


    def Subscription_info(self,User_name):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        self.ID = cursor.execute("SELECT user_id FROM Log_in WHERE user_name=?", (User_name,)).fetchall()
        info_of_book = cursor.execute("SELECT books_id, s_date, e_date FROM Subscription WHERE user_id=?",
                                      (self.ID[0][0],)).fetchall()
        if info_of_book:
            book_id = []
            start_book = []
            end_book = []
            for book in info_of_book:
                book_id.append(book[0])
                start_book.append(book[1])
                end_book.append(book[2])
            name_of_book = []
            name = []
            date_dic=[]
            for x in range(len(book_id)):
                name_of_book = cursor.execute("SELECT name FROM Books WHERE id=?", (book_id[x],)).fetchall()
                name.append(name_of_book[0][0])
            for x in range(len(book_id)):
                print(f"Name={name[x]}")
                print(f"book id={book_id[x]}")
                print(f"start date={start_book[x]}")
                print(f"end date={start_book[x]}")
                print("-" * 22)
                date_dic.append((name[x],book_id[x],start_book[x],start_book[x]))
            return date_dic
        else:
            print("You are not borrowing a book ")



    def remove_book(self,book_id):
        db = Data_Base()
        conn = sqlite3.connect(db._get_url())
        cursor = conn.cursor()
        check_id=cursor.execute("SELECT id FROM Books WHERE id=?",(book_id,)).fetchall()
        if check_id!=[]:
            del_book=cursor.execute("DELETE FROM Books WHERE id=?",(book_id,)).fetchall()
            conn.commit()
            return 1
        else:
            return 0


