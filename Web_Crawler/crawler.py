# Author:
# Pham Quoc Huy - 1512209
# Vu The Huy - 1512213

from queue import Queue
from threading import Thread
import time
import os
import sys
import re
import requests
from bs4 import BeautifulSoup

root = "./data/crawl/root/"

# Define function to extract text from html.
def extractText(soup):
        # Remove invisible tags from html.
        invisibleTags = soup.find_all(['style', 'script'])
        # Loop to extract invisible tags.
        for invisibleTag in invisibleTags:
            invisibleTag.extract()
        
        return ''.join(soup.stripped_strings)

# Define function to extract urls from html .
def extractUrl(soup, filter, limitLengthUrl):
    # Find every a tag (link tag).
    taga = soup.find_all('a', href = True)
    result = []
    
    for tag in taga:
        url = tag["href"]
        # Append if url in limit length and pass the filter.
        if (len(url) < limitLengthUrl and len(re.findall(filter, url)) == 0):
            result.append(url.lower())
    return result

# Define function to get title of html.
def getTitle(soup):
    # Find tag 'title'
    result = soup.find('title').get_text()
    # Delete some special character.
    # In Windows 10 OS. Can not create a file with below character.
    result = ''.join(re.findall("[^\\\/:*?\"><|]", result))
    return result

# Define function to crawl.
def process(url):
    # Directory to save file.
    global root
    try:
        # Request content of web from server.
        html = requests.get(url).text

        # Parse content of web with BeautifulSoup.
        soup = BeautifulSoup(html, 'html.parser')

        # Get title of html.
        title = getTitle(soup)

        # Get text of html.
        text = extractText(soup)

        # Remove if url is css|js|gif|jpg|png|mp3|mp4|3gp|audio|wav|flac|zip|gz|youtube or length > 256
        urls = extractUrl(soup, "\.(css|js|gif|jpg|png|mp3|mp4|3gp|audio|wav|flac|zip|gz|youtube)", 256)
        
        # Write html file.
        with open(root + title + '.html', 'w') as f:
            f.write('html')
        
        # Write txt file.
        with open(root + title + '.txt', 'w') as f:
            f.write(text)

        # Wite log file to storge used url.
        with open("./Log.txt", "a") as f:
            f.write(url +'\n')
        
        return urls
    except:
        pass
    return []

# Define function to run thread to process url.
def runThread(id, newUrl, usedUrl, urlPools):
    while True:
        # Get url form list of new url.
        url = newUrl.get()

        # Finished process of thread if get none from list new url.
        if url == None:
            newUrl.task_done()
            break
        
        # Processing if url not in list of url was crawed
        if url not in usedUrl:
            # Add url in list of url was crawed
            usedUrl.add(url)
            # Calling process function
            urls = process(url)
            # Add urls in pool
            urlPools[id].extend(urls)
        # Finished process
        
        newUrl.task_done()
        print('Crawler ' + str(id) + ' finish process with link: ' + url +\
              '. Log at: ' + time.strftime("%d/%m/%Y %H:%M:%S ", time.gmtime()))
   
    print('\nCrawler ' + str(id) + ' finish job at ' + \
           time.strftime("%d/%m/%Y %H:%M:%S ", time.gmtime()))

################################################################################
# Main
def main():
    # Default properties. It can be changed by cml arg.
    # cml arg through program: crawler.py maxDepth numberOfCrawler seed
    MAX_DEPTH = 7 #setting max depth default
    NUMBER_OF_CRAWLER = 7 #setting number of crawler default
    SEED = "https://vnexpress.net/" #setting seed to craw default

    # Setting with command line
    if len(sys.argv) == 4:
        MAX_DEPTH = int(sys.argv[1])
        NUMBER_OF_CRAWLER = int(sys.argv[2])
        SEED = sys.argv[3]
    
    # Create the dicrectory to storge file
    curDir = os.getcwd()
    for i in root[2:-1].split('/'):
        try:
            os.mkdir(i)
        except:
            pass
        finally:
            os.chdir(i)
    os.chdir(curDir)

    # Create queue and set to storge url
    newUrl = Queue()
    usedUrl = set()

    urlPools = []
    threads = []
    # Create threads
    for i in range(NUMBER_OF_CRAWLER):
        urlPools.append([])
        t = Thread(target=runThread, args = (i , newUrl, usedUrl, urlPools))
        t.start()
        threads.append(t)
    
    newUrl.put(SEED)
    i = 0
    # Processing if depth < max depth
    while i < MAX_DEPTH:
        # Wait for all crawler done_task()
        newUrl.join()
        i += 1
        # Colect url from pool and update the queue
        updateQueue = []
        for element in urlPools:
            updateQueue.extend(element)
            element = []
        for url in set(updateQueue):
            if url not in usedUrl:
                newUrl.put(url)
    
    # Put None to queue. Release the threads
    for i in range(NUMBER_OF_CRAWLER):
        newUrl.put(None)
    for t in threads:
        t.join()
    
    print("FINISH CRAWLLING AT " + time.strftime("%d/%m/%Y %H:%M:%S ", time.gmtime()))

main()
