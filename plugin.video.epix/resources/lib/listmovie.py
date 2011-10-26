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

genreURL = 'http://www.epixhd.com/ajax/psr-landing/genre/'
alphaURL = 'http://www.epixhd.com/ajax/psr-landing/letter/'
BASE = 'http://www.epixhd.com'

################################ Movie listing
def LIST_FEATURE():
    data = common.getURL(BASE)
    url =  BASE + re.compile('flashvars.xmlPath = "(.*?)";').findall(data)[0]
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    for item in tree.findAll('movie'):
        url = item.find('moviepage').string
        name = item.find('title').string
        thumb = item.find('poster').string
        common.addDir(name,'movie','MOVIE_VIDEOS',url,thumb)
        #common.addVideo(name,url,thumb)
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_POP():
    url = 'http://www.epixhd.com/all-movies/'
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    for item in tree.find('div',attrs={'id':'am-top-posters'}).findAll('a'):
        url = item['href']+'/'
        name = item['href'].replace('/','').replace('-',' ').title()
        thumb = item.find('img')['src'].replace('thumbs/','')
        common.addDir(name,'movie','MOVIE_VIDEOS',url,thumb,thumb)
        #common.addVideo(name,url,thumb,thumb)
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_STUNTS():
    for i in range(1,350):
        common.addDir(str(i),'listmovie','LIST_STUNT',str(i))
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_COLLECTIONS():
    data = common.getURL(BASE)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    for item in tree.findAll('a',attrs={'class':'showhomepagestunt'}):
        name = item.string
        common.addDir(name,'listmovie','LIST_STUNT',item['stunt_id'])
    xbmcplugin.endOfDirectory(pluginhandle)

def LIST_POP2():
    LIST_STUNT('63')

def LIST_RECENT():
    LIST_STUNT('55')
    
def LIST_STUNT(id=common.args.url):
    url = 'http://www.epixhd.com/ajax/getstuntlimited/?stunt_id='+id+'&limit=72'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for movie in jsondata['rs']:
        movie = jsondata['rs'][movie]
        print movie
        common.addDir(movie['title'],'movie','MOVIE_VIDEOS','/'+movie['short_name']+'/')
        #common.addVideo(movie['title'],'/'+movie['short_name']+'/')    
    xbmcplugin.endOfDirectory(pluginhandle)  

def LIST_ALPHA():
    url = alphaURL + '1/1/1/'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for url,name in jsondata['all_items'].iteritems():
        if name == 'ALL':
            name = '(ALL)'
        common.addDir(name,'listmovie','LIST_ALPHA_FILTERED',url)
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)
    
def LIST_ALPHA_FILTERED():
    url = alphaURL + common.args.url + '/1/4000/'
    data = common.getURL(url)
    jsondata = demjson.decode(data)
    for movie in jsondata['content']:
        try: thumb = movie['movie_playerposter'].replace('thumbs/','')
        except: thumb = ''
        common.addDir(movie['movie_title'],'movie','MOVIE_VIDEOS',movie['movie_url'],thumb,thumb)
        #common.addVideo(movie['movie_title'],movie['movie_url'],thumb,thumb)
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
        try: thumb = movie['movie_playerposter'].replace('thumbs/','')
        except: thumb = ''
        common.addDir(movie['movie_title'],'movie','MOVIE_VIDEOS',movie['movie_url'],thumb,thumb)
        #common.addVideo(movie['movie_title'],movie['movie_url'],thumb,thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    
def LIST_QUEUE():
    url = 'http://www.epixhd.com/epx/ajax/myqueue/'
    data = common.getURL(url,useCookie=True)
    jsondata = demjson.decode(data)
    for movie in jsondata['queue']:
        try: poster = movie['poster'].replace('thumbs/','')
        except: poster = ''
        try: fanart = movie['playerposter'].replace('thumbs/','')
        except: fanart = ''
        common.addDir(movie['title'],'movie','MOVIE_VIDEOS','/'+movie['short_name']+'/',poster,fanart)
    xbmcplugin.endOfDirectory(pluginhandle)
