import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import demjson
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

BASE_URL = 'http://www.hgtv.com/full-episodes/package/index.html'
BASE = 'http://www.hgtv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    db_shows = []
    sections=tree.findAll('ol',attrs={'id':'fe-list'})
    for section in sections:
        lists = section.findAll('li',recursive=False)
        for list in lists:
            shows = list.findAll('li')
            for show in shows:
                url = BASE+show.find('a',attrs={'class':'button'})['href']
                showname = show.find('h2').string.strip()
                if showname.startswith('HGTV '):
                    showname = showname[5:]
                if db==True:
                    db_shows.append((showname, 'hgtv', 'show', url))
                else:
                    common.addShow(showname, 'hgtv', 'show', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def show(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    sections=tree.find('ul',attrs={'class':'channel-list'})
    if sections:
        sections = sections.findAll('li',recursive=False)
        for section in sections:
            name = section.find('h4').contents[1].strip()
            if common.args.name in name and common.args.name <> name:
                name = name.replace(common.args.name,'').strip().strip('-').strip(',').strip()
            url = section.find('a')['href']
            if 'http://' not in url:
                url = BASE+url
            common.addDirectory(name, 'hgtv', 'videos', url)
        common.setView('seasons')
    else:
        xml_url=getShowXML_URL(data)
        if xml_url:
            videos(xml_url=xml_url)
        else:
            backup_url = tree.find('ul', attrs={'class' : "button-nav"})
            if backup_url:
                if len(backup_url) > 2:
                    show(backup_url.findAll('a')[1]['href'])
            else:
                backup2_url = tree.find('li', attrs={'class' : "tab-past-season"})
                if backup2_url:
                    show(backup2_url.a['href'])



def getShowXML_URL(data):
    showID=re.compile("var snap = new SNI.HGTV.Player.FullSize\('.+?','(.+?)', ''\);").findall(data)
    if len(showID)<1:
        showID=re.compile("var snap = new SNI.HGTV.Player.FullSize\('.+?','(.+?)', '.+?'\);").findall(data)
    if len(showID)<1:
        showID=re.compile("var snap = new SNI.HGTV.Player.FullSize\('.+?','(.+?)'\);").findall(data)
    print showID
    if len(showID)>0:
        return 'http://www.hgtv.com/hgtv/channel/xml/0,,'+showID[0]+',00.xml'
    else:
        return False
        
def videos(url=common.args.url,xml_url=False):
    if not xml_url:
        data = common.getURL(url)
        xml_url=getShowXML_URL(data)
    data = common.getURL(xml_url)
    tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    videos = tree.findAll('video')
    for video in videos:
        name = video.find('clipname').string
        showname = video.find('relatedtitle').string
        if not showname:
            showname=''
        duration = video.find('length').string
        thumb = video.find('thumbnailurl').string.replace('_92x69','_480x360')
        plot = video.find('abstract').string
        link = video.find('videourl').string
        playpath = link.replace('http://wms.scrippsnetworks.com','').replace('.wmv','')
        url = 'rtmp://flash.scrippsnetworks.com:1935/ondemand?ovpfv=1.1 swfUrl="http://common.scrippsnetworks.com/common/snap/snap-3.0.3.swf" playpath='+playpath
        infoLabels={ "Title":name,
                     "Duration":duration,
                     #"Season":season,
                     #"Episode":episode,
                     "Plot":plot,
                     "TVShowTitle":showname
                     }
        common.addVideo(url,name,thumb,infoLabels=infoLabels)
    common.setView('episodes')