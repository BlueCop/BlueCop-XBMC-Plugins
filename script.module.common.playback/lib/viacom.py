import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime


################################ Common
def getURL( url ):
    try:
        print 'Viacom Module --> getURL :: url = '+url
        txdata = None
        txheaders = {
            #'Referer': 'http://www.thedailyshow.com/videos/',
            'X-Forwarded-For': '12.13.14.15',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)',	
        }
        req = urllib2.Request(url, txdata, txheaders)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        error = 'Error code: '+ str(e.code)
        xbmcgui.Dialog().ok(error,error)
        print 'Error code: ', e.code
        return False
    else:
        return link

################################ Play Video
                
def GETVIDEO(url):
        data = getURL(url)
        if 'spike.com' in url:
                try:
                    configurl=re.compile('\("CONFIG_URL", (.+?)\);').findall(data)[0]
                except:
                    configurl=re.compile('value="CONFIG_URL=(.+?)" />').findall(data)[0]     
                url = 'http://www.spike.com'+configurl.replace('"','').replace('%26','&')
                data = getURL(url)
                swfurl = 'http://media.mtvnservices.com/player/release/'+re.compile('>http://media.mtvnservices.com/player/release/(.+?)<').findall(data)[0]
                feeds=re.compile('<feed>(.+?)</feed>').findall(data)
                if len(feeds) > 1:
                    url = feeds[1]
                else:
                    url = feeds[0]
                data = getURL(url)
                uris=re.compile("<media:content.+?url='(.+?)'").findall(data)
                stacked_url = 'stack://'
                for uri in uris:
                        rtmp = GRAB_RTMP(uri,swfurl)
                        stacked_url += rtmp.replace(',',',,')+' , '
                stacked_url = stacked_url[:-3]
                return stacked_url
        if 'atom.com' or 'nick.com' in url:
                uri = 'mgid' + re.compile('mgid(.+?)[\'|"]').findall(data)[0]
                url = 'http://media.mtvnservices.com/player/config.jhtml?uri='+uri+'&group=entertainment&type=network'
                data = getURL(url)
                swfurl = 'http://media.mtvnservices.com/player/release/'+re.compile('>http://media.mtvnservices.com/player/release/(.+?)<').findall(data)[0]
                url = re.compile('<feed>(.+?)</feed>').findall(data)[0].replace('&amp;','&')
                data = getURL(url).replace('\n','')
                uris=re.compile('<media:content.+?url="(.+?)[\'|"]').findall(data)
                stacked_url = 'stack://'
                for uri in uris:
                        rtmp = GRAB_RTMP(uri,swfurl)
                        stacked_url += rtmp.replace(',',',,')+' , '
                stacked_url = stacked_url[:-3]
                return stacked_url
        if 'tvland.com' in url:
                uri = 'mgid' + re.compile('http://media.mtvnservices.com/mgid(.+?)"').findall(data)[0]
                url = 'http://www.tvland.com/feeds/video_player/mrss/?uri='+uri
                data = getURL(url)
                #swfurl = 'http://media.mtvnservices.com/player/release/'+re.compile('>http://media.mtvnservices.com/player/release/(.+?)<').findall(data)[0]
                swfurl = 'http://media.mtvnservices.com/player/prime/mediaplayerprime.1.1.4.swf'
                uris=re.compile('<media:content.+?url="(.+?)"').findall(data)
                stacked_url = 'stack://'
                for uri in uris:
                        rtmp = GRAB_RTMP(uri,swfurl)
                        stacked_url += rtmp.replace(',',',,')+' , '
                stacked_url = stacked_url[:-3]
                return stacked_url
        else:
                uri = 'mgid' + re.compile('mgid(.+?)"').findall(data)[0].split('?')[0]
                url = 'http://media.mtvnservices.com/player/config.jhtml?uri='+uri+'&group=entertainment&type=network'
                data = getURL(url)
                uris=re.compile('<media:content.+?url="(.+?)[\'|"]').findall(data)
                #if uris == None:
                #        uris=re.compile("<media:content.+?url='(.+?)'").findall(data)
                swfurl = 'http://media.mtvnservices.com/player/release/'+re.compile('>http://media.mtvnservices.com/player/release/(.+?)<').findall(data)[0]
                stacked_url = 'stack://'
                for uri in uris:
                        uri = uri.replace('&amp;','&')
                        rtmp = GRAB_RTMP(uri,swfurl)
                        stacked_url += rtmp.replace(',',',,')+' , '
                stacked_url = stacked_url[:-3]
                return stacked_url

        
################################ Grab rtmp        

def GRAB_RTMP(url,swfurl):
        data = getURL(url)
        data = data.replace('<![CDATA[','').replace(']]>','')
        widths = re.compile('width="(.+?)"').findall(data)
        heights = re.compile('height="(.+?)"').findall(data)
        bitrates = re.compile('bitrate="(.+?)"').findall(data)
        if 'rtmp://' or 'rtmpe://' in data:
            rtmps = re.compile('<src>rtmp(.+?)</src>').findall(data)
            http = False
        else:
            rtmps = re.compile('<src>http(.+?)</src>').findall(data)
            http = True
        mpixels = 0
        mbitrate = 0
        for rtmp in rtmps:
                print rtmp
                marker = rtmps.index(rtmp)
                if widths[marker] <> 'null' or heights[marker] <> 'null':
                    w = int(widths[marker])
                    h = int(heights[marker])
                else:
                    w = 1
                    h = 1
                try:
                    bitrate = int(bitrates[marker])
                except:
                    bitrate = 1
                if bitrate == 0:
                    continue
                else:
                    pixels = w * h
                    if pixels > mpixels or bitrate > mbitrate:
                            mpixels = pixels
                            mbitrate = bitrate
                            if http == True:
                                furl = 'http'+rtmp.replace('&amp;','&')
                            elif http == False:
                                furl = 'rtmp'+ rtmp + " swfurl=" + swfurl + " swfvfy=true"
        return furl
