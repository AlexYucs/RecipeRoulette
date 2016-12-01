# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from random import randint
import lxml

import urllib
import time


class foodSites:

    #Ingredient string and urls
    ingstr = ""
    linklist = ""

    #function finds the ingredients at a given url for allrecipes.com
    def ingredList(self, site):
        htmlpg = urllib.urlopen("http://allrecipes.com"+site)
        soup = BeautifulSoup(htmlpg,"lxml")
        ingr = soup.findAll('li', class_= "checkList__line")
        fin = ""
        for ele in ingr:
            if ele.span.get_text()!="" and ele.span.get_text()!="Add all ingredients to list":
                fin = fin + ele.span.get_text()+ "\n"
        return str(fin)

    #function randomly picks a link from the main page of the chosen recipe type at allrecipes.com
    def findLink(self, theLink):
        htmlpg = urllib.urlopen(theLink)
        soup = BeautifulSoup(htmlpg,"lxml")
        print(soup.title.get_text())
        recip_list = soup.findAll('article', class_="grid-col--fixed-tiles")
        listr = []
        for element in recip_list:
                if element.a is not None:
                        if "/recipe/" in element.a["href"]:
                                print(element.a["href"])
                                listr.append(element.a["href"])
        num = randint(0, len(listr)-1)
        print("\n")
        return listr[num]

    #function initializes the ingredients and url lists
    def initList(self):
        global ingstr
        global linklist
        link1 = "http://allrecipes.com/recipes/446/main-dish/beef/"
        #link2 = "http://allrecipes.com/recipes/16954/main-dish/chicken/"
        #link3 = "http://allrecipes.com/recipes/17245/main-dish/pasta/"
        
        chosen = self.findLink(link1)
        ingstr = "Ingredients: \n"+self.ingredList(chosen)
        linklist = "http://allrecipes.com" + chosen + "\n"

        #chosen = self.findLink(link2)
        #ingstr = ingstr + self.ingredList(chosen)
        #linklist = linklist + "http://allrecipes.com" + chosen + "\n"

        #chosen = self.findLink(link3)
        #ingstr = ingstr + self.ingredList(chosen)
        #linklist = linklist + "http://allrecipes.com" + chosen + "\n"

        print(ingstr)

    #return ingredient list
    def getIngred(self):
        global ingstr
        return ingstr

    #return url list
    def getSites(self):
        global linklist
        return linklist
