import urllib, urllib2
import os, re, sys, md5, string
import xbmc, xbmcgui, xbmcplugin

from elementtree.ElementTree import *
from pyamf.remoting.client import RemotingService

baseurl = 'http://www.scifi.com/rewind/'

class ElementWrapper:
    def __init__(self, element):
        self._element = element
    def __getattr__(self, tag):
        if tag.startswith("__"):
            raise AttributeError(tag)
        return self._element.findtext(tag)

class RSSWrapper(ElementWrapper):

    def __init__(self, feed):
        channel = feed.find("channel")
        ElementWrapper.__init__(self, channel)
        self._items = channel.findall("item")

    def __getitem__(self, index):
        return ElementWrapper(self._items[index])

def getHTML( url ):
        try:
                print 'USA --> getHTML :: url = '+url
                req = urllib2.Request(url)
                req.addheaders = [('Referer', 'http://www.usa.com'),
                                  ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)')]
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
        except urllib2.URLError, e:
                print 'Error code: ', e.code
                return False
        else:
                return link


def shows():
        url = 'http://www.scifi.com/rewind/playlist.xml'
        showsxml=getHTML(url)
        xml = ElementTree(fromstring(showsxml))
        shows = []
        for item in xml.getroot().findall('series'):
                show = []
                show.append(item.find('id').text)
                show.append(item.find('name').text)
                show.append(baseurl + item.find('thumbnailUrl').text)
                shows.append(show)
        return shows

def episodes(url):
        rssurl = 'http://video.scifi.com/player/feeds/?level=' + url + '&type=placement&showall=1'
        showsxml=str(getHTML(rssurl))
        tree = ElementTree(fromstring(showsxml))
        feed = RSSWrapper(tree.getroot())
        print "FEED", repr(feed.title)
        episodes = []
        for item in feed:
                episode = []
                url = item.link.replace('&dst=rss|scififullepisode|','')
                episode.append(url)                
                name = item.title.title()
                episode.append(name)
                episode.append('')#Blank thumb right now don't know how to handle : in rss values
                episodes.append(episode)
        return episodes
    

def getsmil(vid):
        gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
                     referer='http://video.nbcuni.com/embed/player_3-x/External.swf',
                     user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
                     )
        ClipAll_service = gw.getService('getClipInfo.getClipAll')
        geo  ="US"
        num1 = " "
        #num2 = "-1"
        response = ClipAll_service(vid,geo,num1)#,num2)
        print response
        if 'errordis' in response.keys():
                xbmcgui.Dialog().ok(xbmc.getLocalizedString(30005), xbmc.getLocalizedString(30005))
                return
        else:
                url = 'http://video.nbcuni.com/' + response['clipurl']
                return url


#get from amf server congfig. 
def getrtmp():
        #rtmpurl = 'rtmp://cp37307.edgefcs.net:443/ondemand'
        gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
                     referer='http://video.nbcuni.com/embed/player_3-x/External.swf',
                     user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
                     )
        ClipAll_service = gw.getService('getConfigInfo.getConfigAll')
        #Not sure where this number is coming from need to look further at action script.
        num1 = "19100"
        response = ClipAll_service(num1)
        rtmphost= response['akamaiHostName'] 
        app = response['akamaiAppName']
        rtmpurl = 'rtmp://'+rtmphost+':443/'+app
        return rtmpurl

    

#constant right now. not sure how to get this be cause sometimes its another swf module the player loads that access the rtmp server
def getswfUrl():
        swfUrl = "http://video.nbcuni.com/embed/player_3-x/External.swf"
        return swfUrl
