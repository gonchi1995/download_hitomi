#!/usr/bin/python3

from bs4 import BeautifulSoup   # For Scraping
import concurrent.futures       # For multi thread
import requests                 # For download
import os                       # For control directory
import sys                      # For using args
import argparse                 # For ArgumentPerser

# Select Subdomain
def select_subdomain(url: str) -> str:
    list = ['aa', 'ba'] # Candidates of Subdomain
    req = requests.get(url) # Get page
    soup = BeautifulSoup(req.text, "html.parser")   # Instance of Scraping
    
    # Find subdomain
    for i in list:
        sample_url = "https://"+ i + soup.find("div", class_="img-url").string[3:]
        req2 = requests.get(sample_url)
        if req2.status_code == 200:
            return i
    
    return None

# List url
def list_url(gallerynum: str, subdomain: str) -> bool:
    # Gallery page url
    gallery_url = "https://hitomi.la/reader/"+ gallerynum + ".html"
    # Request gallery page
    gallery_page = requests.get(gallery_url)

    # Request failed
    if gallery_page.status_code != 200:
        print("Requests Failed")
        exit(-1)

    gallery_soup = BeautifulSoup(gallery_page.text, "html.parser")  # Use BeautifulSoup
    list_imgurl = gallery_soup.findAll("div", class_="img-url")     # Find class "img-url"
    # Create list
    str_imgurl = list()
    changed_imgurl = list()
    
    str_imgurl = [imgurl.string for imgurl in list_imgurl]     # Get string data
    changed_imgurl = ["https://"+ subdomain + imgurl[3:] for imgurl in str_imgurl] # Create url
    gallery_dir = "galleries/"+gallerynum   # Gallery directory

    # Make gallery directory
    if os.path.exists(gallery_dir) == False:
        os.mkdir(gallery_dir)

    # Write list to file
    with open(gallery_dir + "/img_url.txt", "w") as listfile:
        for imgurl in changed_imgurl:
            print(imgurl)
            listfile.write(imgurl + "\n")

    
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

    # ArgumentParser
    parser = argparse.ArgumentParser(description="Download image file from hitomi.la")

    # Add argument
    parser.add_argument('gallerynum', type=str, help='Number of gallery')
    parser.add_argument('-t', '--threadnum', default=25, type=int, help='Number of thread')
    parser.add_argument('--list-only', action='store_true', help='Execute list only.')
    parser.add_argument('--download-only', action='store_true', help='Execute download only.')
    args = parser.parse_args()
    gallerynum = args.gallerynum
    threadnum = args.threadnum

    # List url
    if args.download_only == False:
        print("Execute list url.")
        subdomain = select_subdomain("https://hitomi.la/reader/"+ gallerynum + ".html")
        list_url(gallerynum, subdomain)

    if args.list_only == False:
        print("Execute download.")
        # Directory and File
        gallery_dir = "galleries/"+args.gallerynum
        url_list_file = "img_url.txt"

        # Read image url list
        with open(gallery_dir+"/"+url_list_file, "r") as f:
            urls = f.read()

        url_list = urls.split("\n") # Split list by newline character
        url_list.remove("")         # Remove blank line

        url_list = remove_list(url_list)    # Remove downloaded image url

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=threadnum)   # Instance of thread pool
        # Execute download
        for url in url_list:
            executor.submit(download, url)  # Multi thread
            #download(url)                  # Single thread

        print("Download is successful.")
