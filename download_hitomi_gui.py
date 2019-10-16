#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import os
import sys
import threading
import tkinter as tk
import tkinter.ttk as ttk
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# url_type
FAILED = 0
AA = 1
BA = 2
CA = 3
READER = 0
WEBP = 4
EXT_WEBP = 8

""" 
def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = Toplevel1 (root)
    hitomi_download_support.init(root, top)
    root.mainloop()
     """
""" 
w = None
def create_Toplevel1(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = tk.Toplevel (root)
    top = Toplevel1 (w)
    hitomi_download_support.init(w, top, *args, **kwargs)
    return (w, top)
"""
""" 
def destroy_Toplevel1():
    global w
    w.destroy()
    w = None
"""
class DownloaderWindow:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'

        top.geometry("300x200+524+276")
        top.title("hitomi downloader")
        top.configure(background="#d9d9d9")

        self.menubar = tk.Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        top.configure(menu = self.menubar)

        self.Button1 = tk.Button(top)
        self.Button1.place(relx=0.367, rely=0.35, height=33, width=79)
        self.Button1.configure(activebackground="#ececec")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(command=lambda:self.clicked_button())
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''download''')

        self.Label1 = tk.Label(top)
        self.Label1.place(relx=0.167, rely=0.15, height=26, width=35)
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(text='''URL:''')

        self.Entry1 = tk.Entry(top)
        self.Entry1.place(relx=0.3, rely=0.15,height=21, relwidth=0.613)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(insertbackground="black")

        self.exelog = tk.StringVar()

        self.Label2 = tk.Label(top)
        self.Label2.place(relx=0.133, rely=0.7, height=26, width=212)
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(textvariable=self.exelog)
    
        self.exelog2 = tk.StringVar()

        self.Label3 = tk.Label(top)
        self.Label3.place(relx=0.133, rely=0.8, height=26, width=212)
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(textvariable=self.exelog2)

        self.root = top

    def list_url(self, gallery_url):
        # ギャラリーページのurlから画像表示ページのurlを推測する
        display_url = gallery_url.split("/")
        display_url[3] = "reader"
        display_url = "/".join(display_url)
        self.ref_url = display_url

        # HTTPリクエストヘッダセット
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        req = urllib.request.Request(display_url)
        req.add_header("User-Agent", user_agent)

        # 画像表示ページ取得
        try:
            with urllib.request.urlopen(req) as res:
                data = res.read()
        except urllib.error.URLError as e:
            print(e)
            return None

        # 画像表示ページURLを取得する
        soup = BeautifulSoup(data, "html.parser")
        urllist = soup.findAll("div", class_="img-url")
        urllist = [i.string for i in urllist]

        # url_typeを決定する
        url_type = FAILED
        end_flag = False
        for head in ["aa", "ba", "ca"]:
            for reader in ["reader", "webp"]:
                for ext in ["webp", ""]:
                    # aa.hitomi.laかba.hitomi.laかca.hitomi.laか
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
            if end_flag:
                break


        urllist2 = list()
        if url_type == FAILED:  # 失敗
            print("Get URL list FAILED")
            return None

        # URLタイプによってURLを変える
        if (url_type & 0x03) == AA:
            url_head = "https://aa"
        elif (url_type & 0x03) == BA:
            url_head = "https://ba"
        else:
            url_head = "https://ca"
        
        if (url_type & 0x04) == WEBP:
            url_reader = "webp"
        else:
            url_reader = "reader"

        for url in urllist:
            url2 = url.split(".")
            url2[0] = url_head
            url2 = ".".join(url2)
            url2 = url2.split("/")
            url2[3] = url_reader
            url2 = "/".join(url2)
            if (url_type & 0x08) == EXT_WEBP:
                url2 += ".webp"
            urllist2.append(url2)
        
        return urllist2

    def download(self, img_url):
        # User Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"

        # リクエストヘッダ設定
        req = urllib.request.Request(img_url)
        req.add_header("User-Agent", user_agent)
        req.add_header("Referer", self.ref_url)

        # ダウンロード
        try:
            # GETリクエストを飛ばす
            with urllib.request.urlopen(req) as res:
                data = res.read()
        except urllib.error.URLError as e:
            print(e)
            # 失敗数を1増やす
            self.fail_cnt = self.fail_cnt + 1
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
            # 成功数を1増やす
            self.success_cnt = self.success_cnt + 1
            self.exelog2.set("{}/{}".format(self.success_cnt, self.img_cnt))
            return True

    def exec_download(self, img_url):
        self.exelog.set("downloading..." + img_url.split("/")[-1])
        print("downloading..." + img_url)
        ret = self.download(img_url)
        return ret

    # ボタンイベント
    def clicked_button(self):
        thread = threading.Thread(target=self.multi_download)
        thread.start()

    # マルチスレッドでダウンロード
    def multi_download(self):
        self.success_cnt = 0
        self.fail_cnt = 0
        urllist = self.list_url(self.Entry1.get())
        if urllist == None:
            return False
        self.img_cnt = len(urllist)
        exec = ThreadPoolExecutor(max_workers=25)
        futures = [exec.submit(self.exec_download, url) for url in urllist]
        self.exelog.set("成功数：{}　失敗数：{}".format(self.success_cnt, self.fail_cnt))
        self.exelog.set("")

    def start(self):
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    window = DownloaderWindow(root)
    window.start()




