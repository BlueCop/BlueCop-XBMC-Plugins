#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmcplugin
import xbmc
import xbmcgui
import os.path
import sys
import urllib
import string
import demjson
import re
from BeautifulSoup import BeautifulSoup
import resources.lib.common as common

pluginhandle = common.pluginhandle

# 501-POSTER WRAP 503-MLIST3 504=MLIST2 508-FANARTPOSTER 
confluence_views = [500,501,502,503,504,508]

BASE = 'http://www.epixhd.com'

################################ Movie and Extras listing
def MOVIE_VIDEOS():
    url = BASE + common.args.url
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:fanart = tree.find('div',attrs={'class':'more-images wallpapers'}).find('img')['src'].replace('thumbs/','')
    except:
        try:fanart = re.compile("\('(.*?)'\)").findall(tree.find('div',attrs={'id':'playerposter'})['style'])[0]
        except:fanart = ''
    data = common.getURL('http://www.epixhd.com/epx/ajax/theater/soloplayer'+common.args.url)
    if 'This movie is not currently playing on EPIX' not in data and 'outofwindow' not in data:
        movietitle = tree.find('h1',attrs={'class':'movie_title'}).string
        plot = tree.find('div',attrs={'class':'synP'}).renderContents()
        tags = re.compile(r'<.*?>')
        plot = tags.sub('', plot).strip()
        mpaa = tree.find('span',attrs={'id':'rating'})['class']
        genre = tree.find('span',attrs={'class':'genres'}).findAll('span',recursive=False)
        if len(genre) == 3:
            year = int(tree.find('span',attrs={'class':'genres'}).contents[0].strip())
            runtime = genre[1].string.replace('mins','').strip()
        else:
            year = int(genre[0].string)
            runtime = genre[2].string.replace('mins','').strip()
        for item in genre:
            print item
        poster = tree.find('div',attrs={'class':'more-images posters'}).find('img')['src'].replace('thumbs/','') 
        infoLabels={ "Title": movietitle,
                    'plot':plot,
                    'mpaa':mpaa,
                    'duration':runtime,
                    'year':year}
        common.addVideo('Play Movie: '+movietitle,common.args.url,poster,fanart,infoLabels=infoLabels)    
    for item in tree.findAll('div',attrs={'class':re.compile('more-videos ')}):
        name = item.find('h5').string
        thumb = item.find('img')['src'].replace('thumbs/','')
        common.addDir(name,'movie','MOVIE_EXTRAS',url,thumb,fanart)
    xbmcplugin.endOfDirectory(pluginhandle)

def MOVIE_EXTRAS():
    data = common.getURL(common.args.url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:fanart = tree.find('div',attrs={'class':'more-images wallpapers'}).find('img')['src'].replace('thumbs/','')
    except:
        try:fanart = re.compile("\('(.*?)'\)").findall(tree.find('div',attrs={'id':'playerposter'})['style'])[0]
        except:fanart = ''
    for item in tree.findAll('div',attrs={'class':re.compile('more-videos ')}):
        name = item.find('h5').string
        if name == common.args.name:
            for extra in item.findAll('a'):
                print extra.string
                if extra.string == None or extra.string == 'more' or extra.string == 'less':
                    continue
                thumb = re.compile('"src", "(.*?)"\)').findall(extra['onmouseover'])[0].replace('thumbs/','') 
                common.addVideo(extra.string.strip(),BASE+extra['href'],thumb,fanart,extra=True)
    xbmcplugin.endOfDirectory(pluginhandle)
