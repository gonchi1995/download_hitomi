#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import sys

args = sys.argv

if len(args) < 3:
    print("Usage %s GalleryNumber initial\n" % args[0])
    exit(-1)

gallery_url = args[1]
gallery_url = "https://hitomi.la/reader/" + args[1] + ".html"
gallery_moji  = args[2]

gallery_page = requests.get(gallery_url)

if gallery_page.status_code != 200:
    print("Requests Failed\n")
    exit(-1)

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

