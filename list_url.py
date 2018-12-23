#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os, sys

# ドメイン選択
def select_moji(url):
    list = ["aa", "ba"] # aa, bb
    # ページ情報をリクエスト
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
         
    # ページのリクエストが通れば通ったほうがドメイン
    for i in list:  
        sample_url = "https://" + i + soup.find("div", class_="img-url").string[3:]
        req2 = requests.get(sample_url)
        if req2.status_code == 200:
            return i

    return None


if __name__ == "__main__":
    
    args = sys.argv

    # 引数チェック
    if len(args) < 2:
        print("Usage %s GalleryNumber\n" % args[0])
        exit(-1)
    # ギャラリーナンバー
    gallery_num = args[1]
    # ページのurl
    gallery_url = "https://hitomi.la/reader/" + args[1] + ".html"
    # 画像のページをリクエスト
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

    gallery_dir = "galleries/%s" % gallery_num

    if os.path.exists(gallery_dir) == False:
        os.mkdir(gallery_dir)

    # ファイルに書き込み
    with open(gallery_dir + "/img_url.txt", "w") as img_file:
        for imgurl in changed_imgurl:
            print(imgurl)
            img_file.write(imgurl + "\n")

