import urllib, urllib2
import os, re, sys, md5, string
import xbmc, xbmcgui, xbmcplugin

from elementtree.ElementTree import *
from pyamf.remoting.client import RemotingService

baseurl = 'http://www.usanetwork.com'
fullurl = 'http://www.usanetwork.com/fullepisodes/'
weburl = 'http://www.nbc.com/Video/library/webisodes/'

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
        url = 'http://www.usanetwork.com/globalNav.xml'
        showsxml=getHTML(url)
        xml = ElementTree(fromstring(showsxml))
        shows = []
        for item in xml.getroot().findall('menu/item')[5]:
                show = []
                show.append(item.get('url'))
                name = item.get('name').title()
                show.append(name)
                if name == 'Burn Notice':
                        thumb = 'http://www.usanetwork.com/fullepisodes/images/bn.gif'
                elif name == 'Monk':
                        thumb = 'http://www.usanetwork.com/fullepisodes/images/monk.gif'
                elif name == 'Psych':
                        thumb = 'http://www.usanetwork.com/fullepisodes/images/psych.gif'
                elif name == 'In Plain Sight':
                        thumb = 'http://www.usanetwork.com/fullepisodes/images/ips.gif'
                else:
                        thumb = ''
                show.append(thumb)
                shows.append(show)
        #Need better way to get show list missing Starter Wife and couldn't find a feed for Dr Steve-O
        #show = []        
        #show.append('http://video.usanetwork.com/player/feeds/?level=743701&type=placement&showall=1')
        #show.append('Starter Wife')
        #show.append('http://www.usanetwork.com/fullepisodes/images/sw.gif')
        #shows.append('show')
        return shows

def episodes(url):
        url = baseurl + url
        page = getHTML(url)
        rssurl=re.compile('var _rssURL = "(.+?)";').findall(page)[0].replace('%26','&')
        showsxml=str(getHTML(rssurl))
        tree = ElementTree(fromstring(showsxml))
        feed = RSSWrapper(tree.getroot())
        print "FEED", repr(feed.title)
        episodes = []
        for item in feed:
                episode = []
                url = item.link.replace('&dst=rss|usa|','')
                episode.append(url)                
                name = item.title.title()
                episode.append(name)
                episode.append('')#Blank thumb right now don't know how to handle ':' in rss values
                episodes.append(episode)
        return episodes
    

def getsmil(vid):
        gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
                     referer='http://www.usanetwork.com/[[IMPORT]]/video.nbcuni.com/outlet/extensions/inext_video_player/video_player_extension.swf',
                     user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
                     )
        ClipAll_service = gw.getService('getClipInfo.getClipAll')
        geo  ="inside"
        num1 = "www.usanetwork.com"
        num2 = "-1"
        response = ClipAll_service(vid,geo,num1,num2)
        if 'errordis' in response.keys():
                xbmcgui.Dialog().ok(xbmc.getLocalizedString(30005), xbmc.getLocalizedString(30005))
                return
        else:
                url = 'http://video.nbcuni.com/' + response['clipurl']
                return url


#get from amf server congfig. gateway: http://video.nbcuni.com/amfphp/gateway.php Service:
def getrtmp():
        #rtmpurl = 'rtmp://8.18.43.101/ondemand?_fcs_vhost=cp35588.edgefcs.net'
        gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
                     referer='http://www.usanetwork.com/[[IMPORT]]/video.nbcuni.com/outlet/extensions/inext_video_player/video_player_extension.swf',
                     user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
                     )
        ClipAll_service = gw.getService('getConfigInfo.getConfigAll')
        #Not sure where this number is coming from need to look further at action script.
        num1 = "23012"
        response = ClipAll_service(num1)
        rtmphost= response['akamaiHostName'] 
        app = response['akamaiAppName']
        identurl = 'http://'+rtmphost+'/fcs/ident'
        ident = getHTML(identurl)
        ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
        rtmpurl = 'rtmp://'+ip+'/'+app+'?_fcs_vhost='+rtmphost
        return rtmpurl
    

#constant right now. not sure how to get this be cause sometimes its another swf module the player loads that access the rtmp server
def getswfUrl():
        swfUrl = "http://www.usanetwork.com/[[IMPORT]]/video.nbcuni.com/outlet/extensions/inext_video_player/video_player_extension.swf"
        return swfUrl



#OLD USA CODE

def showhtml():
        shows = getHTML(fullurl)
        clean = re.compile('\<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)\>').sub( '\n', shows)
        match=re.compile('<img src="(.+?)" border="0" height="142" width="276"></td>').findall(clean)
        shows = []
        for url in match:
                show = []
                url = baseurl + url
                show.append(url)
                if 'monk.gif' in url:
                        name = 'Monk'
                        cat = 'monk'
                elif 'psych.gif' in url:
                        name = 'Pysch'
                        cat = 'psych'
                elif 'bn.gif' in url:
                        name = 'Burn Notice'
                        cat = 'burnnotice'
                elif 'ips.gif' in url:
                        name = 'In Plain Sight'
                        cat = 'inplainsight'
                elif 'sw.gif' in url:
                        name = 'Starter Wife'
                        cat = 'starterwife'
                elif 'steveo.gif' in url:
                        name = 'Dr. Steve O'
                        cat = 'drsteve-o'
                addDir(name,cat,1,url)
                
def episodeshtml(cat):
        shows = getHTML(fullurl)
        clean = re.compile('\<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)\>').sub( '\n', shows)
        match=re.compile('<a href="(.+?)" target="new">(.+?)</a>').findall(clean)
        for url,name in match:
                if '<img' in name:
                        continue
                if cat in url:
                        pidsplit = url.split('id=')
                        pid = pidsplit[1]
                        addDir(name,pid,2,'')
