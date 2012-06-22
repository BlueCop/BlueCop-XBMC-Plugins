#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import xbmcplugin
import xbmc
import xbmcgui
import os.path
import sys
import urllib
import resources.lib.common as common
import re
import appfeed

pluginhandle = common.pluginhandle
confluence_views = [500,501,502,503,504,508]

################################ Library listing    
def LIBRARY_ROOT():
    common.addDir('Movies','library','LIBRARY_LIST_MOVIES','https://www.amazon.com/gp/video/library/movie?show=all&sort=alpha')
    common.addDir('Television','library','LIBRARY_LIST_TV','https://www.amazon.com/gp/video/library/tv?show=all&sort=alpha')
    xbmcplugin.endOfDirectory(pluginhandle)

def WATCHLIST_ROOT():
    common.addDir('Movies','library','WATCHLIST_LIST_MOVIES','https://www.amazon.com/gp/video/watchlist/movie?show=all&sort=DATE_ADDED')
    common.addDir('Television','library','WATCHLIST_LIST_TV','https://www.amazon.com/gp/video/watchlist/tv?show=all&sort=DATE_ADDED')
    xbmcplugin.endOfDirectory(pluginhandle)

def WATCHLIST_LIST_MOVIES():
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    url = common.args.url
    data = common.getURL(url,useCookie=True)
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    data = scripts.sub('', data)
    style = re.compile(r'<style.*?style>',re.DOTALL)
    data = style.sub('', data)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'innerItem','id':True})
    totalItems = len(videos)
    for video in videos:
        asin = video['id']
        appfeed.ADD_MOVIE(asin,isPrime=True,inWatchlist=True)
    viewenable=common.addon.getSetting("viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"movieview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)
    
def WATCHLIST_LIST_TV():
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    url = common.args.url
    data = common.getURL(url,useCookie=True)
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    data = scripts.sub('', data)
    style = re.compile(r'<style.*?style>',re.DOTALL)
    data = style.sub('', data)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'innerItem','id':True})
    totalItems = len(videos)
    for video in videos:
        asin = video['id']
        appfeed.ADD_SEASON(asin,isPrime=True,inWatchlist=True)
    viewenable=xbmcplugin.getSetting(pluginhandle,"viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"showview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_LIST_MOVIES():
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    url = common.args.url
    data = common.getURL(url,useCookie=True)
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    data = scripts.sub('', data)
    style = re.compile(r'<style.*?style>',re.DOTALL)
    data = style.sub('', data)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'lib-item','asin':True})
    totalItems = len(videos)
    for video in videos:
        asin = video['asin']
        appfeed.ADD_MOVIE(asin,isPrime=False)
    viewenable=common.addon.getSetting("viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"movieview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_LIST_TV():
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    url = common.args.url
    data = common.getURL(url,useCookie=True)
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    data = scripts.sub('', data)
    style = re.compile(r'<style.*?style>',re.DOTALL)
    data = style.sub('', data)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'lib-item','asin':True})
    totalItems = len(videos)
    for video in videos:
        asin = video['asin']
        appfeed.ADD_SEASON(asin,'library','LIBRARY_EPISODES',isPrime=False)
    viewenable=xbmcplugin.getSetting(pluginhandle,"viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"showview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_EPISODES():
    LIST_EPISODES(owned=True)
    
def LIST_EPISODES(owned=False):
    episode_url = common.BASE_URL+'/gp/product/'+common.args.url
    xbmcplugin.setContent(int(sys.argv[1]), 'Episodes') 
    data = common.getURL(episode_url,useCookie=owned)
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    data = scripts.sub('', data)
    style = re.compile(r'<style.*?style>',re.DOTALL)
    data = style.sub('', data)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodes = tree.find('div',attrs={'id':'avod-ep-list-rows'}).findAll('tr',attrs={'asin':True})
    del tree
    for episode in episodes:
        if owned:
            purchasecheckbox = episode.find('input',attrs={'type':'checkbox'})
            if purchasecheckbox:
                continue
        asin = episode['asin']
        appfeed.ADD_EPISODE(asin,isPrime=False)
    viewenable=xbmcplugin.getSetting(pluginhandle,"viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"episodeview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)