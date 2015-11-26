# __author__ = Dinesh Kannan
# A single threaded focused web crawler with options for including new threads to improve performance

# ARGUMENTS : Seed page, Key phrase to be searched
# RETURNS : List of relevant urls from the seedpage upto a depth of 5 and upto 1000 unique urls

# This web crawler follows strict filtering policies respecting the Robots Exclusion Protocol

# Import external modules
from urlparse import urlparse
from robotparser import RobotFileParser
from bs4 import BeautifulSoup
import urllib
import sys
import time
import threading
import socket

socket.setdefaulttimeout = 10     # Global default timeout for long and irresponsive pages
PYTHONIOENCODING = 'utf-8'        # Set utf-8 encoding for data processing
sys.setrecursionlimit(1000000)	  # Maximum recursion limit

urlRequestQ = []				  # The global request Queue for Urls
visitedUrls = []				  # List of visited urls
blocked = []					  # List of all blocked urls
domainFilter = 'en.wikipedia.org/wiki/' # For filtering non-English and non-Wikipedia pages



# ARGUMENTS : seedpage, keyphrase
# Appends seed to the URLRequestQ and calls crawl function
def crawler(seedPage,keyPhrase):
	seedPage = seedPage + '0'
	urlRequestQ.append(seedPage)
	crawl(keyPhrase)


# ARGUMENTS : keyphrase
# RETURNS : List of relevant URLs
# Does the main processing of all the URLs starting from seed. Calls filterModule() to filter out pages. Recursively calls itself until 
# required depth of 1000 unique URLs is reached.

def crawl(keyPhrase):
	
	URL = urlRequestQ.pop()
	depth = int(URL[-1])
	URL = URL[0:-1]
	domain = urlparse(URL).scheme+"://"+urlparse(URL).netloc
	pageObject = filterModule(URL, keyPhrase)
	
	if pageObject != 'NULL':

		htmlPage = urllib.urlopen(URL).read()
		parsedHtml = BeautifulSoup(htmlPage, 'html.parser')

		for link in parsedHtml.find_all('a', href = True):
			address = link['href'].encode('utf-8')
			if '#' not in address:
				if address[0] == '/':
					if address[1] == '/':
						address = "https:" + address + str(depth)	
					else:
						address = domain + address + str(depth)
					urlRequestQ.append(address)
				elif address[0:5] == 'http':
					urlRequestQ.append(address+str(depth))	
					
		visitedUrls.append(URL)
		print URL
		time.sleep(2)
	
	if len(visitedUrls) < 1000 and len(visitedUrls) != 0 and len(urlRequestQ) > 0 and (depth-1) <= 5:
		crawl(keyPhrase)
	else:
		return



# ARGUMENTS : URL, keyphrase
# RETURNS : NULL if the URL is blocked or not relevant, a urllib pageobject otherwise
# Filters the given URL based on conditions in the problem statement and on Robots Exclusion Protocol (robots.txt)

def filterModule(URL, keyPhrase):

	if URL in blocked or URL in visitedUrls:	
		blocked.append(URL)
		return 'NULL'

	if ':' in urlparse(URL).path:
		blocked.append(URL)
		return 'NULL'

	if domainFilter+"Main_Page" in URL:
		blocked.append(URL)
		return 'NULL'

	if urlValidity(URL) and domainFilter in URL:
		
		if checkRobots(URL):
	
			time.sleep(1)
			pageObject = urllib.urlopen(URL)
			if searchKeyPhrase(URL, keyPhrase, pageObject):
				return pageObject
			else:
				blocked.append(URL)
				return 'NULL'
	else:
		blocked.append(URL)
		return 'NULL'


# ARGUMENTS : URL
# RETURNS : True if the URL is valid (i.e. An existing webpage with RESPONSE CODE = 200)
# Validates if there are actual contents and can be opened without any network or connection errors
def urlValidity (URL):
	
	try:
		time.sleep(1)
		pageObject = urllib.urlopen(URL)
		if pageObject.getcode() == 200:
			return True
	except:
		blocked.append(URL)
		return False

	
# ARGUMENTS : URL
# RETURNS : True if the URL is crawlable (i.e. allowed by robots.txt)
# Checks robots.txt of a webserver to determine the crawlability of its page
def checkRobots(URL):

	time.sleep(1)
	parsed = urlparse(URL)
	robotsUrl = parsed.scheme + "://"+ parsed.netloc+"/robots.txt"
	robotParser = RobotFileParser()
	robotParser.set_url(robotsUrl)
	robotParser.read()
	result = robotParser.can_fetch("*",URL)
	return result


# ARGUMENTS : URL , keyphrase, urllib pageobject
# RETURNS : True if the keyphrase is found in the page's contents (irrespective of case)
def searchKeyPhrase(URL, keyPhrase, pageObject):

	htmlPage = pageObject.read()
	parsedHtml = BeautifulSoup(htmlPage, 'html.parser')
	contents = parsedHtml.get_text().encode('ascii','ignore')
	if keyPhrase.lower() in contents.lower():
		return True
	else:
		return False


# Main function whose thread calls the crawler(). More threads can be added to improve performances
if __name__ == "__main__":
	URL = sys.argv[1]
	keyPhrase = sys.argv[2]
	thread1 = threading.Thread(target= crawler, args = (URL, keyPhrase))
	thread1.start()




