import requests
from bs4 import BeautifulSoup
import csv

page_url=requests.get("https://en.z-library.sk/users/zrecommended")

number_of_bock=int(input("enter number of books:"))


def main(page_url):
    src=page_url.content
    soup=BeautifulSoup(src,"lxml")
    print(src)

main(page_url)