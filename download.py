#!/usr/bin/python3

import concurrent.futures   # For multi thread
import requests             # For download
import os                   # For control directory
import sys                  # For using args

# Remove downloaded image url from list
def remove_list(list: list) -> list:
    
    # Confirm existence of "clearlist.txt"
    if os.path.exists("galleries/%s/clearlist.txt" % (list[0].split("/")[-2])) == False:
        print("clearlist.txt not exist")
        return list # "clearlist.txt" not exist

    
    with open("galleries/{}/clearlist.txt".format(list[0].split('/')[-2]), 'r') as f:
        urls = f.read()
    clear_list = urls.split('\n')   # Split urllist by newline character
    clear_list.remove("")           # Remove blank line from clear list

    # Remove url that is in clearlist from urllist
    for i in clear_list:
        if i in list:
            list.remove(i)

    return list

# Download Images
def download(url: str) -> bool:
    print("downloading..." + url)   # Print download

    # Requests Image
    req = requests.get(url)
    
    # Request is failed
    if req.status_code != 200:
       print("Requests Failed\n")
       return False
   
    directory = "galleries/" + url.split('/')[-2]   # Gallery directory
    filename = url.split('/')[-1]                   # File name

    # Make gallery directory
    if os.path.exists(directory) == False:
        os.mkdir(directory)

    # Write image data
    with open(directory+"/"+filename, "wb") as f:
        f.write(req.content)

    # Add url to clearlist
    if os.path.exists(directory+"/clearlist.txt") == False:
        with open(directory+"/clearlist.txt", "x") as f:
            f.write(url+"\n")
    else:
        with open(directory+"/clearlist.txt", "a") as f:
            f.write(url+"\n")

    return True

# Main
if __name__ == '__main__':
    # Directory and File
    gallery_dir = "galleries/"+sys.argv[1]
    url_list_file = "img_url.txt"

    # Read image url list
    with open(gallery_dir+"/"+url_list_file, "r") as f:
        urls = f.read()

    url_list = urls.split("\n") # Split list by newline character
    url_list.remove("")         # Remove blank line

    url_list = remove_list(url_list)    # Remove downloaded image url

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=25)   # Max thread 100
    # Execute download
    for url in url_list:
        executor.submit(download, url)  # Multi thread
        #download(url)                  # Single thread
