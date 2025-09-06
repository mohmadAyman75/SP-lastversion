import Book
from Data_base import Data_Base
import  stuff
import librarian
import manager
import user
import sqlite3

class User_System():
    def User_System(self):
        print("Welcome in SP library")
        chouice=int(input("1- Create_Account\n2- Log_In\n"))
        #__User_name=input("Enter User Name:") #you shoud add userName here ,you can get it from wep
        #__passwrod=input("Enter password:") #applay all things the same below
        ID = user.User().Log_in("qwe","qwe")  #add data here
        match chouice:
            case 1:
                user.User().create_account()
            case 2:
                if ID[1]==1:#user
                    print("\n1-all Book\n2-search Book\n3-borrow Book\n4-subscription info\n5-Borrowed Books\n6-info return date\n7-manage Account\n8-Exit")
                    choice=int(input("Enter:"))
                    match choice:
                        case 1:
                            print("\n")
                            print(Book.Book().all_book())
                        case 2:
                            Book.Book().search_book()
                        case 3:
                            Book.Book().borrowed_book(*ID[0])
                        case 4:
                            print(user.User().Subscription_info(ID[0]))
                        case 5:
                            print(user.User().get_recent_book(ID[0]))
                        case 6:
                            user.User().info_return_data(*ID[0])
                        case 7:
                            user.User().update_info(*ID[0])
                        case 8:
                            print("You welcome")
                            return 1
                        case _:
                            print("wrong choice..\n")
                            return 0
                elif ID[1]==2:#librarian
                    print("1-help Users\n2-manage Subscription\n3-number copies\n4-lend Book\n5-add Item\n6-subscription info\n7-Exit")
                    choice=int(input("Enter:"))
                    match choice:
                        case 1:
                            librarian.Librarian().manage_user()
                        case 2:
                            librarian.Librarian().update_sub()
                        case 3:
                            librarian.Librarian().manipulate_copies()
                        case 4:
                            librarian.Librarian().lend_book()
                        case 5:
                            librarian.Librarian().add_new_book()
                        case 6:
                            print(stuff.Stuff().Subscription_info("qwe"))
                        case 7:
                            print("you welcome")
                            return 1
                        case _:
                            print("Try again..")
                elif ID[1]==3:
                    chouice=int(input("1-create new stuff account/user account\n2-Remove account\n3-financial\n4-all Book\n5-Exit"))
                    match(chouice):
                        case 1:
                            manager.Manager().add_new()
                        case 2:
                            manager.Manager().remove()
                        case 3:
                            manager.Manager().check_financial()
                        case 4:
                            manager.Manager().over_all_book()
                        case 5:
                            print("You welcome")
                            return 1
                        case _:
                            print("Try again..")
                else:
                    print("Try again..")
            case _:
                print("Try again..")

User_System().User_System()