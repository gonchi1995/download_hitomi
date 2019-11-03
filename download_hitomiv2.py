# coding: utf-8

import urllib.request
import urllib.error
import argparse
import os
import sys
import selenium
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# url_type
FAILED = 0
AA = 1
BA = 2
CA = 3
READER = 0
WEBP = 4
EXT_WEBP = 8

# javascript使用
JS_USED = 1         # ページにjavascript使用
JS_NOT_USED = 0     # ページにjavascriptを使用しない

# ギャラリーのトップページが格納されているディレクトリ
HOME_DIR = "gamecg"

# 画像表示ページのURLを取得
def get_display_url(gallery_url):
    url = gallery_url.split("/")[-1]
    gallery_num = url.split("-")[-1].split(".")[0]
    gallery_ext = url.split("-")[-1].split(".")[-1]

    display_url = gallery_url.split("/")
    display_url[3] = display_url[3] = "reader"
    display_url[4] = gallery_num + "." + gallery_ext
    display_url = "/".join(display_url)

    return display_url


# Referer用URLを取得
def get_refurl(url):
    ref_url = get_display_url(url)

    return ref_url

def chk_disp_page(gallery_url):
    # ギャラリーページのurlから画像表示ページのurlを推測する
    display_url = get_display_url(gallery_url)

    user_agent = "Mozilla/5.0"

    # HTTPリクエストを設定する
    req = urllib.request.Request(display_url)
    req.add_header("User-Agent", user_agent)
    req.add_header("Referer", gallery_url)

    # ページを読み込む
    try:
        with urllib.request.urlopen(req) as res:
            data = res.read()
    except urllib.error.URLError as e:
        print(e)

    # スクレイピングする
    soup = BeautifulSoup(data, "html.parser")
    div = soup.find("div", class_="img-url")

    if div:
        ret = JS_NOT_USED
    else:
        ret = JS_USED

    return ret

# 画像表示ページから画像URLを取得
def list_url(gallery_url):
    # ギャラリーページのurlから画像表示ページのurlを推測する
    display_url = get_display_url(gallery_url)

    # HTTPリクエストヘッダセット
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    req =urllib.request.Request(display_url)
    req.add_header("User-Agent", user_agent)

    # 画像表示ページ取得
    try:
        with urllib.request.urlopen(req) as res:
            data = res.read()
    except urllib.error.URLError as e:
        print(e)
        return None

    # 画像ページのURLを取得する
    soup = BeautifulSoup(data, "html.parser")
    urllist = soup.findAll("div", class_="img-url")
    urllist = [i.string for i in urllist]

    # url_typeを決定する line:35～77 ※改善できそう
    url_type = FAILED
    end_flag = False
    # aa.hitomi.la か ba.hitomi.laか
    for head in ["aa", "ba", "ca"]:
        for reader in ["galleries", "webp"]:
            # 画像が保存されているディレクトリ
            for ext in ["webp", ""]:
                # webpがつくかつかないか
                sample = urllist[0].split(".")
                sample[0] = "https://" + head
                sample = ".".join(sample)
                sample = sample.split("/")
                sample[3] = reader
                sample = "/".join(sample)

                if ext == "webp":
                    sample += ".webp"

                req = urllib.request.Request(sample)
                req.add_header("User-Agent", user_agent)
                req.add_header("Referer", display_url)

                try:
                    ref = urllib.request.urlopen(req)
                except urllib.error.URLError as e:
                    continue
                
                end_flag = True
                ref.close()

                # ページ取得成功した場合url_typeを決定する
                if ext == "webp":
                    url_type = EXT_WEBP
                else:
                    url_type = FAILED
                
                if reader == "reader":
                    url_type |= READER
                elif reader == "webp":
                    url_type |= WEBP
                else:
                    url_type = FAILED
                
                if head == "aa":
                    url_type |= AA
                elif head == "ba":
                    url_type |= BA
                elif head == "ca":
                    url_type |= CA
                else:
                    url_type = FAILED
                
                # url_typeを決定したのでfor文を抜ける
                break

        # 終了フラグが立っている場合は終了する
        if end_flag == True:
            break

    # https://xx.hitomi.la…(.webp)の形にする
    urllist2 = list()
    if url_type == FAILED:  # 失敗の場合
        print("Get URL list FAILED")
        return None
    
    # URLタイプによってURLを変える
    if url_type & AA:
        url_head = "https://aa"
    elif url_type & BA:
        url_head = "https://ba"
    else:
        url_head = "https://ca"

    if url_type & WEBP:
        url_reader = "webp"
    else:
        url_reader = "galleries"

    # URLをリストに追加する
    for url in urllist:
        url2 = url.split(".")
        url2[0] = url_head
        url2 = ".".join(url2)
        url2 = url2.split("/")
        url2[3] = url_reader
        url2 = "/".join(url2)
        if url_type & EXT_WEBP:
            url2 += ".webp"
        urllist2.append(url2)
        
    return urllist2

# ページがjavascriptで画像URLを生成している場合に使用
def list_url2(gallery_url):
    urllist = list()    # URLリスト

    # ギャラリーページのurlから画像表示ページのurlを推測する
    display_url = get_display_url(gallery_url)
    display_url = display_url + "#1"
    
    # Chromeを起動
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=options)

    # 最初の画像ページを取得
    driver.get(display_url)
    data = driver.page_source

    # 最初のページの画像URLを取得
    soup = BeautifulSoup(data, "html.parser")
    image = soup.find("div", id="comicImages").find("img").get("src")
    urllist.append("https:" + image)

    # 画像数を取得
    size = len(soup.find("select", id="single-page-select"))

    for i in range(2, size + 1):
        # 画像表示ページのURLを生成
        url = display_url.split("#")
        url[-1] = str(i)
        url = "#".join(url)

        # 画像ファイルのURLスクレイピング
        driver.get(url)
        data = driver.page_source
        soup = BeautifulSoup(data, "html.parser")
        div = soup.find("div", id="comicImages")
        image = div.find("img")
        image = soup.find("div", id="comicImages").find("img").get("src")
        urllist.append("https:" + image)

        if i == size:
            print("\r{} / {}".format(i, size))          # 最後は改行
        else:
            print("\r{} / {}".format(i, size), end="")
    

    # Chromeを終了
    driver.close()

    return urllist

# 画像をダウンロード
def download(img_url, ref_url, num):
    # User Agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"

    # リクエストヘッダ設定
    req = urllib.request.Request(img_url)
    req.add_header("User-Agent", user_agent)
    req.add_header("Referer", ref_url)

    # ダウンロード
    try:
        # GETリクエストを飛ばす
        with urllib.request.urlopen(req) as res:
            data = res.read()
    except urllib.error.URLError as e:
        print(e)
        return False
    else:
        # ギャラリー番号
        gallery_num = ref_url.split("/")[-1].split(".")[0]

        # ギャラリーのディレクトリがない場合作成する
        if not os.path.exists("galleries/" + gallery_num):
            os.makedirs("galleries/" + gallery_num, 755)

        # ファイル名
        fname = img_url.split("/")[-1]
        ext = fname.split(".")[-1]
        if ext == "webp":
            ext = fname.split(".")[-2]
        
        fname = str(num) + "." + ext

        # ファイルに書き込む
        with open("galleries/" + gallery_num + "/" + fname, "wb") as f:
            f.write(data)

        return True

# ダウンロード実行用関数
def exec_download(img_url, ref_url, num):
    print("downloading..." + img_url)
    ret = download(img_url, ref_url, num)
    return ret

def main():
    # コマンドライン引数設定
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("url", help="gallery page url")         # ギャラリーページのURL
    parser.add_argument("-t", default=25, help="thread count")  # 稼働スレッド数
    args = parser.parse_args()

    # HTTP Referer用URL
    ref_url = get_refurl(args.url)

    print("Check displaypage")
    js_used = chk_disp_page(args.url)

    # 画像のURLをリスト化
    if js_used:
        urllist = list_url2(args.url)
    else:
        urllist = list_url(args.url)

    # 画像URL取得失敗
    if urllist is None:
        print("List Failed")
        sys.exit()

    # マルチスレッドで画像をダウンロード
    executor = ThreadPoolExecutor(max_workers=int(args.t))
    futures = [executor.submit(exec_download, url, ref_url, i) for url, i in zip(urllist, range(len(urllist)))]


if __name__ == "__main__":
    main()
