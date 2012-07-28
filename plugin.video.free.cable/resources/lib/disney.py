import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import resources.lib._common as common

pluginhandle = int(sys.argv[1])
showlist= 'http://watchdisneyxd.go.com/shows'
BASE = 'http://watchdisneyxd.go.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    #div id="showContainer_SH55170916" class="showContainer"
    data = common.getURL(showlist)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.findAll('div',attrs={'class':'showContainer'})
    db_shows = []
    for show in shows:
        name = show.find('a')['title']
        url = show.find('a')['page']
        if db==True:
            db_shows.append((name,'disneyxd','seasons',url))
        else:
            common.addDirectory(name, 'disneyxd', 'seasons', url )
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
        
def seasons(url=common.args.url):
    if common.addoncompat.get_setting('abc_rss')=='true':
        rss=True
    else:
        rss=False
    data = common.getURL(url)
    season_set = makeDict(re.compile('season.set\(\{(.+?)\}\);').findall(data)[0])
    season_url = BASE+season_set['service'].replace('(accesslevel)','1')
    showid = season_set['showid']
    tabs_set = makeDict(re.compile('tabs.set\(\{(.+?)\}\);').findall(data)[0])
    tabs_url = BASE+tabs_set['service'].replace('(accesslevel)','1')
    content_set = makeDict(re.compile('content.set\(\{(.+?)\}\);').findall(data)[0])
    content_url = BASE+content_set['service'].replace('(accesslevel)','1')
    for season in BeautifulSoup(common.getURL(season_url), convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('a'):
        seasonid = season['seasonid']
        season_name = season.string
        tabs_url = tabs_url.replace('(seasonid)',seasonid)
        tab_data = BeautifulSoup(common.getURL(tabs_url), convertEntities=BeautifulSoup.HTML_ENTITIES)
        print tab_data.prettify()
        tab_data = tab_data.find('a')
        playlistid = tab_data['playlistid']
        playlistcount = tab_data['playlistcount']
        rss_url = tabs_set['rss'].replace('(playlistid)',playlistid).replace('-1/-1/-1',str(seasonid)+'/-1/-1')
        content_url = content_url.replace('(seasonid)',seasonid).replace('(playlistid)',playlistid).replace('(start)','0').replace('(size)',str(playlistcount)) 
        if rss:
            common.addDirectory(season_name, 'disneyxd', 'episodesRSS', rss_url)
        else:
            common.addDirectory(season_name, 'disneyxd', 'episodes', content_url)
        
    #CLIPS
    try:
        tabs_set = makeDict(re.compile('tabs.set\(\{(.+?)\}\);').findall(data)[1])
        content_set = makeDict(re.compile('content.set\(\{(.+?)\}\);').findall(data)[1])
        content_url = BASE+content_set['service']
        tabs_url = BASE+tabs_set['service']
        tabs = BeautifulSoup(common.getURL(tabs_url), convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('a')
        for tab in tabs:
            name = tab.string
            playlistid = tab['playlistid']
            playlistcount = tab['playlistcount']
            rss_url = tabs_set['rss'].replace('(playlistid)',playlistid)
            content_url = content_url.replace('view=showsplaylist','view=showsfplaylist').replace('(playlistid)',playlistid).replace('(start)','0').replace('(size)',str(playlistcount)).replace('(max)',str(playlistcount))
            if rss:
                common.addDirectory(name, 'disneyxd', 'episodesRSS', rss_url)
            else:
                common.addDirectory(name, 'disneyxd', 'episodes', content_url)
    except:pass
    common.setView('seasons')
    
def makeDict(sets):
    print sets
    sets = sets.split(', ')
    season_dict={}
    for set in sets:
        split = set.replace('"','').split(':',1)
        try:season_dict[split[0].strip()]=split[1].strip()
        except:pass
    return season_dict

def episodes(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.findAll('div',attrs={'class':'tile'})
    for item in menu:
        link = item.find('div',attrs={'class':'tile_title'}).find('a')
        name = link.string
        url = link['href']
        thumb = item.find('img')['src']
        try: description = item.find('div',attrs={'class':'tile_desc'}).string
        except: description = ''
        show_tile_sub = item.find('div',attrs={'class':'show_tile_sub'}).string.split('|')
        airDate = show_tile_sub[1].replace(' Aired on ','').strip()
        duration = show_tile_sub[0].strip()
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="disneyxd"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Plot":description,
                     "premiered":common.formatDate(airDate,'%m/%d/%y'),
                     "Duration":duration,
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')
        
def play(url=common.args.url):
    finalurl=False
    vid=url.split('/')[-2]
    videolinks = 'http://abc.go.com/vp2/ws/s/contents/2012/videos/009/001/-1/-1/-1/%s/-1/-1?v=08.00' % vid
    data = common.getURL(videolinks)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    finalurl = tree.find('assets').find('asset').string
    if finalurl:    
        item = xbmcgui.ListItem(path=finalurl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
