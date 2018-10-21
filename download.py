#!/usr/bin/python3

import requests, asyncio, os

def remove_list(list):
    
    if os.path.exists(list[0].split("/")[-2] + "/" + "clearlist.txt") == False:
        return list

    with open(list[0].split("/")[-2] + "/" + "clearlist.txt", "r") as f:
        urls = f.read()
    clear_list = urls.split("\n")
    clear_list.remove("")

    
    for i in clear_list:
        if i in list:
            list.remove(i)

    return list

async def download(url):
    print("downloading..." + url)
    req = requests.get(url)

    if req.status_code != 200:
        print("Requests Failed\n")
        return False

    directory = url.split("/")[-2]
    filename = url.split("/")[-1]

    if os.path.exists(directory) == False:
        os.mkdir(directory)
        
    with open(directory + "/" + filename, "wb") as f:
        f.write(req.content)

    if os.path.exists(directory + "/" + "clearlist.txt") == False:
        with open(directory + "/" + "clearlist.txt", "x") as f:
            f.write(url+"\n")
    else:
        with open(directory + "/" + "clearlist.txt", "a") as f:
            f.write(url+"\n")
         
    await asyncio.sleep(0.3)
    return True
    
with open("img_url.txt", "r") as f:
    urls = f.read()

url_list = urls.split("\n")
url_list.remove("")

url_list = remove_list(url_list)

loop = asyncio.get_event_loop()

coros = [download(url) for url in url_list]
futures = asyncio.gather(*coros)
loop.run_until_complete(futures)
print(futures.result())
loop.close()
