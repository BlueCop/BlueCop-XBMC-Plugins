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
from BeautifulSoup import BeautifulSoup
import resources.lib.common as common

pluginhandle = common.pluginhandle

# 501-POSTER WRAP 503-MLIST3 504=MLIST2 508-FANARTPOSTER 
confluence_views = [500,501,502,503,504,508]

genreURL = 'http://www.epixhd.com/ajax/psr-landing/genre/'
alphaURL = 'http://www.epixhd.com/ajax/psr-landing/letter/'
BASE = 'http://www.epixhd.com'

################################ Movie listing
def LIST_POP():
    url = 'http://www.epixhd.com/all-movies/'
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    for item in tree.find('div',attrs={'id':'am-top-posters'}).findAll('a'):
        print item
        url = item['href']+'/'
        name = item['href'].replace('/','').replace('-',' ').title()
        thumb = item.find('img')['src']
        common.addVideo(name,url,thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    
def LIST_POP2():
    url = 'http://www.epixhd.com/ajax/getstuntlimited/?stunt_id=63&limit=36'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for movie in jsondata['rs']:
        movie = jsondata['rs'][movie]
        common.addVideo(movie['title'],'/'+movie['short_name']+'/')    
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_RECENT():    
    url = 'http://www.epixhd.com/ajax/getstuntlimited/?stunt_id=55&limit=36'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for movie in jsondata['rs']:
        movie = jsondata['rs'][movie]
        common.addVideo(movie['title'],'/'+movie['short_name']+'/')    
    xbmcplugin.endOfDirectory(pluginhandle)  

def LIST_ALPHA():
    url = alphaURL + '1/1/1/'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for url,name in jsondata['all_items'].iteritems():
        common.addDir(name,'listmovie','LIST_ALPHA_FILTERED',url)
    xbmcplugin.endOfDirectory(pluginhandle)
    
def LIST_ALPHA_FILTERED():
    url = alphaURL + common.args.url + '/1/4000/'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for movie in jsondata['content']:
        common.addVideo(movie['movie_title'],movie['movie_url'],movie['movie_playerposter'])
    xbmcplugin.endOfDirectory(pluginhandle)
        
def LIST_GENRE():
    url = genreURL + '1/1/1/'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for url,name in jsondata['all_items'].iteritems():
        common.addDir(name,'listmovie','LIST_GENRE_FILTERED',url)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)
    
def LIST_GENRE_FILTERED():
    url = genreURL + common.args.url + '/1/4000/'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for movie in jsondata['content']:
        common.addVideo(movie['movie_title'],movie['movie_url'],movie['movie_playerposter'])
    xbmcplugin.endOfDirectory(pluginhandle)

        
      

        


