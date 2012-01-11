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

pluginhandle = common.pluginhandle
confluence_views = [500,501,502,503,504,508]

################################ Library listing    
def LIBRARY_ROOT():
    common.addDir('Movie Library','library','LIBRARY_LIST_MOVIES','https://www.amazon.com/gp/video/library/movie?show=all&sort=alpha')
    common.addDir('Television Library','library','LIBRARY_LIST_TV','https://www.amazon.com/gp/video/library/tv?show=all&sort=alpha')
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_LIST_MOVIES():
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    url = common.args.url
    data = common.getURL(url,useCookie=True)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'lib-item','asin':True})
    totalItems = len(videos)
    for video in videos:
        asin = video['asin']
        movietitle = video.find('',attrs={'class':'title'}).a.string
        url = common.BASE_URL+video.find('div',attrs={'class':'title'}).a['href']
        thumb = video.find('img')['src'].replace('._SS160_','')
        fanart = thumb.replace('.jpg','._BO354,0,0,0_CR177,354,708,500_.jpg')       
        #if xbmcplugin.getSetting(pluginhandle,'enablelibrarymeta') == 'true':
        #    asin2,movietitle,url,poster,plot,director,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart,isprime,watched,favor = getMovieInfo(asin,movietitle,url,poster,isPrime=False)
        #    actors = actors.split(',')
        #    infoLabels = { 'Title':movietitle,'Plot':plot,'Year':year,'premiered':premiered,
        #                   'rating':stars,'votes':votes,'Genre':genres,'director':director,
        #                   'studio':studio,'duration':runtime,'mpaa':mpaa,'cast':actors}
        #else:
        infoLabels = { 'Title':movietitle}
        common.addVideo(name,url,thumb,fanart,infoLabels=infoLabels,totalItems=totalItems)
    viewenable=common.addon.getSetting("viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"movieview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_LIST_TV():
    url = common.args.url
    data = common.getURL(url,useCookie=True)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    videos = tree.findAll('div',attrs={'class':'lib-item','asin':True})
    totalItems = len(videos)
    for video in videos:
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        asin = video['asin']
        name = video.find('',attrs={'class':'title'}).a.string
        thumb = video.find('img')['src'].replace('._SS160_','')
        if '[HD]' in name: isHD = True
        else: isHD = False
        url = common.BASE_URL+video.find('div',attrs={'class':'title'}).a['href']
        #if xbmcplugin.getSetting(pluginhandle,'enablelibrarymeta') == 'true':
        #    asin2,season,episodes,plot,creator,runtime,year,network,actors,genres,stars,votes,HD,TVDBbanner,TVDBposter,TVDBfanart = getShowInfo(url,asin,isHD)
        #    actors = actors.split(',')
        #    infoLabels={'Title': name,'Plot':plot,'year':year,'rating':stars,'votes':votes,
        #                'Genre':genres,'Season':season,'episode':episodes,'studio':network,
        #                'duration':runtime,'cast':actors,'TVShowTitle':name,'credits':creator}
        #    if year <> 0: infoLabels['premiered'] = str(year)
        #else:
        infoLabels = { 'Title':name}
        common.addDir(name,'library','LIBRARY_EPISODES',url,thumb,thumb,infoLabels,totalItems)
    viewenable=xbmcplugin.getSetting(pluginhandle,"viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"showview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle)

def LIBRARY_EPISODES():
    LIST_EPISODES(owned=True)
    
def LIST_EPISODES(owned=False):
    episode_url = common.args.url
    showname = common.args.name
    thumbnail = common.args.thumb
    xbmcplugin.setContent(int(sys.argv[1]), 'Episodes') 
    data = common.getURL(episode_url,useCookie=owned)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    episodebox = tree.find('div',attrs={'id':'avod-ep-list-rows'})
    episodes = episodebox.findAll('tr',attrs={'asin':True})
    try:season = int(tree.find('div',attrs={'class':'unbox_season_selected'}).string)
    except:
        try:season = int(tree.find('div',attrs={'style':'font-size: 120%;font-weight:bold; margin-top:15px;margin-bottom:10px;'}).contents[0].split('Season')[1].strip())
        except:season = 0
    del tree
    del episodebox
    for episode in episodes:
        if owned:
            purchasecheckbox = episode.find('input',attrs={'type':'checkbox'})
            if purchasecheckbox:
                continue
        asin = episode['asin']
        name = episode.find(attrs={'title':True})['title'].encode('utf-8')
        airDate = episode.find(attrs={'style':'width: 150px; overflow: hidden'}).string.strip()
        try: plot =  episode.findAll('div')[1].string.strip()
        except: plot = ''
        try:episodeNum = int(episode.find('div',attrs={'style':'width: 185px;'}).string.split('.')[0].strip())
        except:episodeNum =0
        if season == 0: displayname =  str(episodeNum)+'. '+name
        else: displayname =  str(season)+'x'+str(episodeNum)+' - '+name
        url = common.BASE_URL+'/gp/product/'+asin
        infoLabels={'Title': name.replace('[HD]',''),'TVShowTitle':showname,
                    'Plot':plot,'Premiered':airDate,
                    'Season':season,'Episode':episodeNum}
        common.addVideo(displayname,url,thumbnail,thumbnail,infoLabels=infoLabels)
    viewenable=xbmcplugin.getSetting(pluginhandle,"viewenable")
    if viewenable == 'true':
        view=int(xbmcplugin.getSetting(pluginhandle,"episodeview"))
        xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=False)