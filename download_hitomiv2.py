import urllib.request
import urllib.error
import argparse
import os
import sys
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# url_type
FAILED = 0
AA_WEBP = 1
AA = 2
BA_WEBP = 3
BA = 4

url = "https://aa.hitomi.la/webp/1449630/025.jpg.webp"
ref_url = "https://hitomi.la/reader/1450055.html"

def list_url(gallery_url):
    # ギャラリーページのurlから画像表示ページのurlを推測する
    display_url = gallery_url.split("/")
    display_url[3] = "reader"
    display_url = "/".join(display_url)
    
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
    end_flag = None
    for head in ["aa", "ba"]:
        # aa.hitomi.la か ba.hitomi.laか
        for ext in ["webp", ""]:
            # webpがつくかつかないか
            sample = urllist[0].split(".")
            sample[0] = "https://" + head
            if not ext == "":
                sample.append(ext)
            sample = ".".join(sample)

            req = urllib.request.Request(sample)
            req.add_header("User-Agent", user_agent)
            req.add_header("Referer", display_url)

            try:
                ref = urllib.request.urlopen(req)
            except urllib.error.URLError as e:
                continue

            ref.close()

            # ページ取得成功した場合url_typeを決定する
            if head == "aa":
                if ext == "webp":
                    url_type = AA_WEBP
                else:
                    url_type = AA
            elif head == "ba":
                if ext == "webp":
                    url_type = BA_WEBP
                else:
                    url_type = BA
            else:
                url_type = FAILED
            # 終了フラグを立てる
            end_flag = True
            break;
        
        # 終了フラグが立っている場合は終了する
        if end_flag == True:
            break;

    # https://xx.hitomi.la…(.webp)の形にする
    urllist2 = list()
    if url_type == FAILED:  # 失敗
        return None
    elif url_type == AA_WEBP: # aa.hitomi.la….webp
        for url in urllist:
            url2 = url.split(".")
            url2[0] = "https://aa"
            url2.append("webp")
            url2 = ".".join(url2)
            urllist2.append(url2)
    elif url_type == AA: # aa.hitomi.la…
        for url in urllist:
            url2 = url.split(".")
            url2[0] = "https://aa"
            url2 = ".".join(url2)
            urllist2.append(url2)
    elif url_type == BA_WEBP: # ba.hitomi.la….webp
        for url in urllist:
            url2 = url.split(".")
            url2[0] = "https://ba"
            url2.append("webp")
            url2 = ".".join(url2)
            urllist2.append(url2)
    elif url_type == BA: # aa.hitomi.la…
        for url in urllist:
            url2 = url.split(".")
            url2[0] = "https://ba"
            url2 = ".".join(url2)
            urllist2.append(url2)
            
    return urllist2

def download(img_url, ref_url):
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
        gallery_num = img_url.split("/")[-2]

        # ギャラリーのディレクトリがない場合作成する
        if not os.path.exists("galleries/" + gallery_num):
            os.makedirs("galleries/" + gallery_num, 755)
        
        # ファイル名
        fname = img_url.split("/")[-1]
        ext = fname.split(".")[-1]
        if ext == "webp":
            # 拡張子がwebp
            remove_webp = fname.split(".")
            del remove_webp[-1]
            fname = ".".join(remove_webp)
        # ファイルに書き込む
        with open("galleries/" + gallery_num + "/" + fname, "wb") as f:
            f.write(data)

        return True

def exec_download(img_url, ref_url):
    print("downloading..." + img_url)
    ret = download(img_url, ref_url)
    return ret
    
def main():
    # コマンドライン引数設定
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("url", help="gallery page url")         # ギャラリーページのURL
    parser.add_argument("-t", default=25, help="thread count")  # 稼働スレッド数
    args = parser.parse_args()

    # 画像のURLをリスト化
    urllist = list_url(args.url)

    # マルチスレッドで画像をダウンロード
    executor = ThreadPoolExecutor(max_workers=args.t)
    futures = [executor.submit(exec_download, url, ref_url) for url in urllist]

    
if __name__ == "__main__":
    main()
