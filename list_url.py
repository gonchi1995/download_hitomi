#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import sys

def select_moji(url):
    list = ["aa", "ba"]
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
         
    for i in list:  
        sample_url = "https://" + i + soup.find("div", class_="img-url").string[3:]
        req2 = requests.get(sample_url)
        if req2.status_code == 200:
            return i

    return None


if __name__ == "__main__":
    
    args = sys.argv

    if len(args) < 2:
        print("Usage %s GalleryNumber initial\n" % args[0])
        exit(-1)

    gallery_url = args[1]
    gallery_url = "https://hitomi.la/reader/" + args[1] + ".html"

    gallery_page = requests.get(gallery_url)

    if gallery_page.status_code != 200:
        print("Requests Failed\n")
        exit(-1)

    gallery_moji = select_moji(gallery_url)

    gallery_soup = BeautifulSoup(gallery_page.text, "html.parser")

    list_imgurl = gallery_soup.findAll("div", class_="img-url")

    str_imgurl = list()
    changed_imgurl = list()

    #for imgurl in list_imgurl:
    #  str_imgurl.append(imgurl.string)
    str_imgurl = [imgurl.string for imgurl in list_imgurl]

    #for imgurl in str_imgurl:
    #  changed_imgurl.append("https://" + gallery_moji + imgurl[3:])
    changed_imgurl = ["https://" + gallery_moji + imgurl[3:] for imgurl in str_imgurl]

    # ファイルに書き込み
    with open("img_url.txt", "w") as img_file:
        for imgurl in changed_imgurl:
            img_file.write(imgurl + "\n")

