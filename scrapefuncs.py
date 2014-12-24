import requests
import bs4 #lxml is faster for scrapes but this is a small job
import re
import csv

###So I'm trying to see if Fabiano was right in all of his "start-em-sit-em" articles###


#first step: get links to all of his start-em sit-em articles on his nfl.com webpage :)
def getLinks():

    page = requests.get("http://www.nfl.com/news/author?id=09000d5d800219d7")
    soup = bs4.BeautifulSoup(page.text)

    links = [a.attrs.get('href') for a in soup.select("div.news-author-headline a[href*=start-em]")]
    dates = [a.text for a in soup.select("a[href*=start-em] + span")]

    return links,dates


#He's been doing this for about 7 years and all I want is this year (the last ten weeks to be exact)
#the previous function gave me ALL of his startem articles
#This is mostly out of fairness. It's hard to predict anything in the beginning of the season.
#this function gets me the start-em sitems article links for the last ten weeks
def wrangleLinks(links, dates):

    newlinks = []
    rightyear = True
    count = 0
    rightdates = []

    while rightyear:
        date = dates[count][-4:]

        if date == "2014": #I just want 2014 articles
            count += 1
            rightdates.append(date)

        else:
            rightyear = False

    newlinks = links[0:len(rightdates)]
    newlinks[-31:] = [] #just want the past ten weeks
    
    return newlinks


#okay now using the links I just got, i need a function that will scrape his guess from each link
#this takes a single url and scrapes what I want
def scrapeTime(url):
    startsits = []
    
    page = requests.get("http://www.nfl.com" + url)
    soup = bs4.BeautifulSoup(page.text)

    group = 'Start'

    #scrape some info from the article headline: week#, playertype (e.g., quarterback,kicker, etc)
    a = soup.select("#news-article-headline")

    if not a:
        return a
    
    a = a[0].text
    a = a.strip()
    a = a.encode('ascii')
    a = re.split(" |\: |", a) #ergh regex

    position = "notsure" #incase there are formating difficulties
    week = "notsure"

    if len(a) == 7:
        week = a[-2]

    if len(a) == 8:
        week = a[-3]
    
    for i in soup.select("div.start-sit-blurb h5"):

        if i.text[0:3] == 'Sit':
            group = 'Sit'

        tx = re.split("-  | vs. |", i.text)
        
        if len(tx) == 3:
            startsits.append(['o', group, week, tx[1]])
            
        if len(tx) == 2:
            startsits.append(['n', group, week, tx[0][1:]])


                             
    return startsits

#then this loops through all the links I scraped and calls the previous function
#ultimately yielding what I want. woop woop
def loopScrapeTime(newlinks):

    startsits = []

    for i in newlinks:
        data = scrapeTime(i)

        if data:
            for j in data:
                startsits.append(j)

    return startsits

#startsits = loopScrapeTime(newlinks)

        
    
###Now scrape actual fantasy scoring data###

#NFL.com CHARGES you for these data, so I scraped them
#from a different website


#function for scraping data from footballdb.com (only provides non zero
#scores for a week)
def scrapeData(url):

    listofdata = []

    page = requests.get(url)
    soup = soup = bs4.BeautifulSoup(page.text)

    for tr in soup.select("tr"):
        templist = []
        for tds in tr.find_all("td"):
            templist.append(tds.text) #extract data from all cells

        listofdata.append(templist)
    
    listofdata[-28:] = [] #28 rows describing scoring
    listofdata[0:2] = [] #two garbage rows
    #some additional munging, want to have team away/home
    for row in listofdata:
        
        if row[2][0] == '@':
            row.append('Away')
            row[2] = row[2][1:]

        else:
            row.append('Home')

    return listofdata


#function that gathers data for each play (aside from kickers/defense)
#by looping the previous function with new urs.

def loopScrapeData(x,y):

    listofdata = []

    

    for i in range(x,y):
        
        url = "http://www.footballdb.com/fantasy-football/index.html?pos=QB&yr=2014&wk="

        url = url + str(i) + "&ppr="      
        data = scrapeData(url)
    

        #Should have used a single for loop in the next section, but it was a last minute change
        for j in data: #function returns 2 garbage rows before real data
            j.append(i)
            j.append('Quarterback') 
            listofdata.append(j)

        url = "http://www.footballdb.com/fantasy-football/index.html?pos=RB&yr=2014&wk="

        url = url + str(i) + "&ppr="      
        data = scrapeData(url)
    
        for j in data: 
            j.append(i)
            j.append("Running Back")
            listofdata.append(j)

        url = "http://www.footballdb.com/fantasy-football/index.html?pos=WR&yr=2014&wk="

        url = url + str(i) + "&ppr="      
        data = scrapeData(url)
    
        for j in data: 
            j.append(i)
            j.append("Wide Receiver")
            listofdata.append(j)

        url = "http://www.footballdb.com/fantasy-football/index.html?pos=TE&yr=2014&wk="

        url = url + str(i) + "&ppr="      
        data = scrapeData(url)
    
        for j in data: 
            j.append(i)
            j.append("Tight End")
            listofdata.append(j)
    
    return listofdata

##func for saving data to csvfiles

def writedata(filename, data):
    with open(filename, "a") as csvfile:
        writer = csv.writer(csvfile)
        for i in data:
            writer.writerow(i)

