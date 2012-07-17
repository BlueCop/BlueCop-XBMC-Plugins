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
showlist= 'http://cdn.abc.go.com/vp2/ws-supt/s/syndication/2000/rss/001/001/-1/-1/-1/-1/-1/-1'
BASE = 'http://abc.go.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(showlist)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    menu=tree.findAll('item')
    db_shows = []
    for item in menu:
        name = item('title')[0].string.encode('utf-8')
        url = item('link')[0].string
        thumb = item('image')[0].string
        if db==True:
            db_shows.append((name,'abc','seasons',url))
        else:
            common.addShow(name, 'abc', 'seasons', url )# , thumb)
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
    season_url = BASE+season_set['service']
    showid = season_set['showid']
    tabs_set = makeDict(re.compile('tabs.set\(\{(.+?)\}\);').findall(data)[0])
    tabs_url = BASE+tabs_set['service']
    content_set = makeDict(re.compile('content.set\(\{(.+?)\}\);').findall(data)[0])
    content_url = BASE+content_set['service']
    for season in BeautifulSoup(common.getURL(season_url), convertEntities=BeautifulSoup.HTML_ENTITIES).findAll('a'):
        seasonid = season['seasonid']
        season_name = season.string
        tabs_url = tabs_url.replace('(seasonid)',seasonid)
        tab_data = BeautifulSoup(common.getURL(tabs_url), convertEntities=BeautifulSoup.HTML_ENTITIES).find('a')
        playlistid = tab_data['playlistid']
        playlistcount = tab_data['playlistcount']
        rss_url = tabs_set['rss'].replace('(playlistid)',playlistid).replace('-1/-1/-1',str(seasonid)+'/-1/-1')
        content_url = content_url.replace('(seasonid)',seasonid).replace('(playlistid)',playlistid).replace('(start)','0').replace('(size)',str(playlistcount)) 
        if rss:
            common.addDirectory(season_name, 'abc', 'episodesRSS', rss_url)
        else:
            common.addDirectory(season_name, 'abc', 'episodes', content_url)
        
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
                common.addDirectory(name, 'abc', 'episodesRSS', rss_url)
            else:
                common.addDirectory(name, 'abc', 'episodes', content_url)
    except:pass
    common.setView('seasons')
    
def makeDict(sets):
    sets = sets.split(',')
    season_dict={}
    for set in sets:
        split = set.replace('"','').split(':',1)
        season_dict[split[0].strip()]=split[1].strip()
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
        u += '&mode="abc"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Plot":description,
                     "premiered":common.formatDate(airDate,'%m/%d/%y'),
                     "Duration":duration,
                     }
        common.addVideo(u,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def seasonsRSS(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    video_rss = menu=tree.find(attrs={'type' : 'application/rss+xml'})['href']
    showid=url.split('?')[0].split('/')[-1]
    url='http://abc.go.com/vp2/s/carousel?service=seasons&parser=VP2_Data_Parser_Seasons&showid='+showid+'&view=season&bust=07000001_3'
    data = common.getURL(url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    seasons=tree.findAll('a')
    for season in seasons:
        seasonid=season['seasonid']
        name=season.string.strip()
        url=video_rss.replace('-1/-1/-1',seasonid+'/-1/-1')
        common.addDirectory(name, 'abc', 'episodes', url )
    common.setView('seasons')

def episodesRSS(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    menu=tree.findAll('item')
    for item in menu:
        namedata = item('title')[0].string.encode('utf-8').split(' Full Episode - ')
        name = namedata[0]
        season = int(namedata[1].split(' - ')[0].split(' | ')[1].replace('s',''))
        episode = int(namedata[1].split(' - ')[0].split(' | ')[0].replace('e',''))
        tvshow = namedata[1].split(' - ')[1] 
        url = item('link')[0].string
        thumb = item('image')[0].string
        airDate = item('pubdate')[0].string.split('T')[0]
        descriptiondata = re.compile('<p>(.+?)</p>').findall(item('description')[0].string)[0].split('<br>')
        description = descriptiondata[0]
        duration = descriptiondata[-2].replace('Duration: ','')
        displayname = '%sx%s - %s' % (str(season),str(episode),name)
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="abc"'
        u += '&sitemode="play"'
        infoLabels={ "Title":name,
                     "Season":season,
                     "Episode":episode,
                     "Plot":description,
                     "premiered":airDate,
                     "Duration":duration,
                     "TVShowTitle":tvshow
                     }
        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')
        
def play(url=common.args.url):
    finalurl=False
    playpath=False
    vid=re.compile('(VD\d*)').findall(url)[0]
    rtmpdata = 'http://cdn.abc.go.com/vp2/ws/s/contents/2003/utils/video/mov/13/9024/%s/432?v=06000007_3' % vid
    data = common.getURL(rtmpdata)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    hosts = tree.findAll('host')
    for host in hosts:
        if host['name'] == 'L3':
            rtmp = 'rtmp://%s/%s' % (host['url'], host['app'])
    filenames = tree.findAll('video')
    hbitrate = -1
    sbitrate = int(common.settings['quality'])
    platpath=False
    for filename in filenames:
        if filename['src'] <> '':
            bitrate = int(filename['bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                playpath = filename['src']
    if playpath:
        swfUrl = 'http://livepassdl.conviva.com/ver/2.27.0.42841/LivePassModuleMain.swf'
        finalurl = rtmp+' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    else:
        plid= re.compile('(PL\d*)').findall(url)[0]
        clipurl = 'http://abc.go.com/vp2/ws/s/contents/1000/videomrss?brand=001&device=001&start=0&limit=100&fk=CATEGORIES&fv='+plid
        data = common.getURL(clipurl)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        for video in tree.findAll('item'):
            if video.find('guid').string == vid:
                finalurl = video.find('media:content')['url']
    if finalurl:    
        item = xbmcgui.ListItem(path=finalurl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
