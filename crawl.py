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
	
	#if len(visitedUrls) < 1000 and len(visitedUrls) != 0 and len(urlRequestQ) > 0 and (depth-1) <= 5:
	
	#	crawl(keyPhrase)
	
	#else:
	#	return