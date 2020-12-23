import requests
import time
import os
import random
from bs4 import BeautifulSoup as bs

'''
Note that this scraper works for a while but eventually gets blocked. As per received instructions, this is not an issue
Care must be taken that this code doesn't modify the folder with the actual data. This creates a new directory called ECT if it does not exist
This performs the mapping of the file names to integers here itself for ease of reading file names
Like most scrapers, this assumes a certain structure of each page it wants to scrape. This was last tested on 11th October, 2020 at 10:00 pm.
If the structure of the "seekingalpha" website was changed after this time, the code will understandably not perform as expected.
'''

val = 0 #Global variable to replace file names with integers for easy reading of names

user_agent_list = [ # List of some user agents for header rotation. Helps in scraper evade detection for slightly longer
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

try: # Creating a new folder to store nested dicts
	os.mkdir(os.path.join(os.getcwd(), "ECT"))
except:
	pass #No handling needed if the folder already exists

def extract_page(url): #Function to extract html file containing only the transcript information
	#Returns True is successful, False if we get Error 403. This decides time to sleep between requests
	global val
	#print("attempting to grab page: " + url)
	#print(url)
	page = requests.get(url, headers={"User-Agent":random.choice(user_agent_list)}) # Requesting the required page with the transcript
	page_html=page.text
	soup = bs(page_html, 'html.parser') # Creating soup object using html parser in Beautiful Soup

	content = soup.find(id="a-body") # This <div id='a-body'> tag marks the start of the transcript
	#print(str(type(content)))
	if str(type(content)) == "<class 'NoneType'>":
	    #print("skipping this link, no content here\n")
	    return False
	else:
	    #File name is ECT to match with assignment requirements. Please ensure that the actual folder of ~4000 files is not changed!
	    #print(content)
	    with open(os.path.join(os.getcwd(),"ECT","Transcript_" + str(val) + ".html"), 'w') as file:
	    	file.write(str(content)) #Writing the html file
	    
	    #print("Transcript_" + str(val) + " sucessfully saved\n")
	    val += 1
	    return True

def extract_scripts(page_no): #Function to extract all transcripts on a certain page
	get_page = "https://seekingalpha.com/earnings/earnings-call-transcripts" + "/" + str(page_no)
	# print("getting page " + origin_page + "\n")
	# print(page_no)

	#Using random User Agent to make it seem that the query is coming from a different browser each time.
	page = requests.get(get_page,headers={"User-Agent":random.choice(user_agent_list)}) # Requesting the required page of list of transcripts.
	#print(page_html)
	page_html=page.text
	# print(page_html)
	soup = bs(page_html, 'html.parser') # Creating soup object using html parser in Beautiful Soup
	alist = soup.find_all("li",{'class':'list-group-item article'}) #This gives all the tags containing links to individual transcripts
	#print(len(alist))
	#print("Here")
	if len(alist)==0: #Retrying once if the previous request yielded Error 403.
		time.sleep(random.randint(10,15)) #Sleeping for 10-15 seconds in order to increase duration between request so that the requests don't seem automated
		page = requests.get(get_page,headers={"User-Agent":random.choice(user_agent_list)})
		page_html=page.text
		# print(page_html)
		soup = bs(page_html, 'html.parser')
		alist = soup.find_all("li",{'class':'list-group-item article'})

	for i in range(0,len(alist)):
	    url_ending = alist[i].find_all("a")[0].attrs['href'] #Getting the url ending for a script
	    url = "https://seekingalpha.com" + url_ending
	    if extract_page(url):
	    	time.sleep(random.randint(3,5)) #Sleeping for 3-5 seconds if successfully scraped a page. 
	    else:
	    	time.sleep(random.randint(5,8)) #Sleeping for 5-8 seconds if error 403 encountered. 



# 334 pages taken since each page has 30 transcripts, and we have to scrape 10,000. So 334*30 = 10,020 transcripts.
for i in range(1,334): #choose what pages of earnings to scrape
	extract_scripts(i)
