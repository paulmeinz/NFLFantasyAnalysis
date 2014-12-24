import requests
import bs4
import re
import csv
import threading
import scrapefuncs as sf


###just going to thread some of the funcs i made in scrapfuncs.py
###otherwise it takes a while

class myThread(threading.Thread):
    def __init__(self, links, years, filename, filename2, output = [], output2 = []):
        threading.Thread.__init__(self)
        self.links = links
        self.years = years
        self.filename = filename
        self.filename2 = filename2
        self.output = output
        self.output2 = output2
        
    def run(self):
        self.output = sf.loopScrapeTime(self.links)
        self.output2 = sf.loopScrapeData(self.years[0], self.years[1])

        sf.writedata(self.filename, self.output)
        sf.writedata(self.filename2, self.output2)
        print "thread complete!"
        
links, dates = sf.getLinks()
newlinks = sf.wrangleLinks(links,dates)

input1 = newlinks[0:20]
input2 = newlinks[20:40]
input3 = newlinks[40:]

yrs1 = [1,6]
yrs2 = [6,11]
yrs3 = [11,16]

#newthreads

one = myThread(input1, yrs1, 'startsit.csv','fantasy2014.csv')
two = myThread(input2, yrs2, 'startsit.csv','fantasy2014.csv')
three = myThread(input3, yrs3, 'startsit.csv','fantasy2014.csv')

#start em!

one.start()
two.start()
three.start()




        



