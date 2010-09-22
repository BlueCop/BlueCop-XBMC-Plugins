import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime


################################ Common
def getURL( url ):
    try:
        print 'CBS Module --> getURL :: url = '+url
        txdata = None
        txheaders = {
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
        #http://www.cbs.com/primetime/csi/video/?pid=YwC5scRGk0iI2zOpssI8EmpRZV4JGDlq
        pid = url.split('pid=')[1]
        url = "http://release.theplatform.com/content.select?format=SMIL&Tracking=true&balance=true&MBR=true&pid=" + pid
        link=getURL(url)
        if 'this content has expired' in link:
            xbmcgui.Dialog().ok('Content Expired','This video is no longer available')
            return False
        elif "rtmp://" in link:
                stripurls = re.compile('<video src="rtmp://(.+?)" system-bitrate=".+?" width="(.+?)" height="(.+?)" profile="(.+?)"').findall(link)
                hpixels = 0
                for stripurl, w, h ,profile in stripurls:
                    pixels = int(w) * int(h)
                    if pixels > hpixels:
                        hpixels = pixels
                        print stripurl
                        cleanurl = stripurl.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').split('<break>')
                        finalurl = "rtmp://" + cleanurl[0]
                        if ".mp4" in cleanurl[1]:
                                playpath = 'mp4:' + cleanurl[1]
                        else:
                                playpath = cleanurl[1].replace('.flv','')
                        swfUrl = "http://www.cbs.com/thunder/player/1_0/chromeless/1_5_1/CAN.swf"
                        finalurl += ' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
        elif "http://" in link:
                stripurl = re.compile('<ref src="http://(.+?)" ').findall(link)
                finalurl = "http://" + stripurl[0]
        return finalurl

