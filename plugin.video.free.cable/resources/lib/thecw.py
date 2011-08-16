import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import httplib
import sys
import os
import re
import demjson

from BeautifulSoup import BeautifulSoup
import resources.lib._common as common

pluginhandle=int(sys.argv[1])

BASE_URL = 'http://www.cwtv.com/cw-video/'
BASE = 'http://www.cwtv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'videoshowslist'}).findAll('li',recursive=False)
    db_shows = []
    for item in menu:
        url = BASE + item.find(attrs={'class':'videothumb'}).find('a')['href']
        thumb = item.find('img')['src']
        showname = item.find(attrs={'class':'videoinfo'}).contents[0].strip()
        if showname == 'More Video':
            continue
        if db==True:
            db_shows.append((showname,'thecw','show',url))
        else:
            common.addDirectory(showname, 'thecw', 'show', url, thumb)
    if db==True:
        return db_shows

def show(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'showtabs'}).findAll('li')
    for item in menu:
        itemurl = url +'<videotab>'+ item['id'].replace('videotab_','')
        name = item.find('a').contents[0].title()
        common.addDirectory(name, 'thecw', 'episodes', itemurl)


def episodes(url=common.args.url):
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    urldata = url.split('<videotab>')
    tabid = int(urldata[1])
    url = urldata[0]
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'showinfo'}).findAll(attrs={'class':'videotabcontents'})
    for item in menu:
        itemid = int(item['id'].replace('videotabcontents_',''))
        if tabid == itemid:
            videos=item.findAll('div',recursive=False)
            for video in videos:
                url = video.find('a')['href'].split('=')[1]
                print url
                thumb = video.find('img')['src']
                name = video.find(attrs={'class':'header'}).string.title()
                hoverinfo = video.find(attrs={'class':'hoverinfo-lower'})('p')[0]
                try:
                    description = hoverinfo.contents[2].strip()
                except:
                    print 'description failure'
                    description = ''
                try:
                    airdate = hoverinfo.contents[0].contents[2].replace('Original Air Date: ','')
                except:
                    print 'airdate failure'
                    airdate=''
                try:
                    duration = hoverinfo.contents[0].contents[4].strip()
                except:
                    print 'duration failure'
                    duration = ''
                try:
                    seasonepisode = hoverinfo.contents[0].contents[0].replace('Season ','').split(', EP. ')
                    season = int(seasonepisode[0])
                    episode = int(seasonepisode[1])
                    displayname = '%sx%s - %s' % (str(season),str(episode),name)
                except:
                    displayname = name
                    season = 0
                    episode = 0
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(url)+'"'
                u += '&mode="thecw"'
                u += '&sitemode="play"'
                item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
                item.setInfo( type="Video", infoLabels={ "Title":name,
                                                         "Season":season,
                                                         "Episode":episode,
                                                         "Plot":description,
                                                         "premiered":airdate,
                                                         "Duration":duration,
                                                         #"TVShowTitle":common.args.name
                                                         })
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)

def play():
    swfurl = 'http://pdl.warnerbros.com/cwtv/digital-smiths/production_player/vsplayer.swf'
    url = 'http://metaframe.digitalsmiths.tv/v2/CWtv/assets/%s/partner/132?format=json' % common.args.url
    data = common.getURL(url)
    items = demjson.decode(data)
    sbitrate = int(common.settings['quality'])
    if sbitrate > 700:
        rtmpdata = items['videos']['ds700']['uri'].split('mp4:')
    if sbitrate < 700:
        rtmpdata = items['videos']['ds500']['uri'].split('mp4:')
    rtmp = rtmpdata[0]
    playpath = 'mp4:'+rtmpdata[1]
    rtmpurl = rtmp+' playpath='+playpath+" swfurl=" + swfurl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

       


