import xbmcplugin
import xbmcgui
import xbmc

import common
import urllib,urllib2
import sys
import re
import os

pluginhandle = int (sys.argv[1])

class Main:

    def __init__( self ):
            name = common.args.name
            pid = common.args.pid
            thumbnail = common.args.thumbnail
            #HD Handler
            if '<break>' in pid:
                breakpid = pid.split('<break>')
                #Default HD 480p
                if (xbmcplugin.getSetting(pluginhandle,"hdquality") == '1'):
                    pid=breakpid[0]
                    name = '480p: ' + name
                #Default HD 720p
                elif (xbmcplugin.getSetting(pluginhandle,"hdquality") == '2'):
                    pid=breakpid[1]
                    name = '720p: ' + name
                elif (xbmcplugin.getSetting(pluginhandle,"hdquality") == '3'):
                    pid=breakpid[2]
                    name = '1080p: ' + name
                #Ask HD Quality
                else:
                    breakpid = pid.split('<break>')
                    dia = xbmcgui.Dialog()
                    ret = dia.select('What do you want to do?', ['Play 480p','Play 720p','Play 1080p','Exit'])
                    #480p selected
                    if (ret == 0):
                            pid=breakpid[0]
                            name = '480p: ' + name
                    #720p selected
                    elif (ret == 1):
                            pid=breakpid[1]
                            name = '720p: ' + name
                    elif (ret == 2):
                            pid=breakpid[2]
                            name = '1080p: ' + name
                    #Exit
                    else:
                            return
            #url containing video link
            url = "http://release.theplatform.com/content.select?format=SMIL&Tracking=true&balance=true&pid=" + pid
            link=common.getHTML(url)
            #Get ad links
            #if (xbmcplugin.getSetting(pluginhandle,"ads") == 'true'):
            #        ads = self.getAds(link)                  
            if "rtmp://" in link:
                    stripurl = re.compile('<ref src="rtmp://(.+?)" ').findall(link)
                    cleanurl = stripurl[0].replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').split('<break>')
                    finalurl = "rtmp://" + cleanurl[0]
                    if ".mp4" in cleanurl[1]:
                            playpath = 'mp4:' + cleanurl[1]
                    else:
                            playpath = cleanurl[1].replace('.flv','')
            elif "http://" in link:
                    stripurl = re.compile('<ref src="http://(.+?)" ').findall(link)
                    finalurl = "http://" + stripurl[0]
                    playpath = ""
                    stream = self.httpDownload(finalurl,name)
                    if stream == 'false':
                        return

            item=xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
            item.setInfo( type="Video",
                         infoLabels={ "Title": name,
                                      #"Season": season,
                                      #"Episode": episode,
                                      #"Duration": duration,
                                      #"Plot": plot,
                                       }
                         )
            swfUrl = "http://www.cbs.com/thunder/player/1_0/chromeless/1_5_1/CAN.swf"
            finalurl += ' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
            #item.setProperty("SWFPlayer", swfUrl)
            #item.setProperty("PlayPath", playpath)
            if xbmcplugin.getSetting(pluginhandle,"dvdplayer") == "true":
                    player_type = xbmc.PLAYER_CORE_DVDPLAYER
            else:
                    player_type = xbmc.PLAYER_CORE_MPLAYER
            ok=xbmc.Player(player_type).play(finalurl, item)

    def httpDownload( self, finalurl, name):
            name = name + '.flv'
            def Download(url,dest):
                            dp = xbmcgui.DialogProgress()
                            dp.create('Downloading','',name)
                            urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
            def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
                            try:
                                            percent = min((numblocks*blocksize*100)/filesize, 100)
                                            dp.update(percent)
                            except:
                                            percent = 100
                                            dp.update(percent)
                            if dp.iscanceled():
                                            dp.close()
            flv_file = None
            stream = 'false'
            if (xbmcplugin.getSetting(pluginhandle,'download') == '0'):
                    dia = xbmcgui.Dialog()
                    ret = dia.select('What do you want to do?', ['Play','Download','Download & Play','Exit'])
                    if (ret == 0):
                            stream = 'true'
                    elif (ret == 1):
                            flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name))
                            Download(finalurl,flv_file)
                    elif (ret == 2):
                            flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name))
                            Download(finalurl,flv_file)
                            stream = 'true'
                    else:
                            return stream
            #Play
            elif (xbmcplugin.getSetting(pluginhandle,'download') == '1'):
                    stream = 'true'
            #Download
            elif (xbmcplugin.getSetting(pluginhandle,'download') == '2'):
                    flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name))
                    Download(finalurl,flv_file)
            #Download & Play
            elif (xbmcplugin.getSetting(pluginhandle,'download') == '3'):
                    flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name))
                    Download(finalurl,flv_file)
                    stream = 'true'            
            if (flv_file != None and os.path.isfile(flv_file)):
                    finalurl =str(flv_file)
            return stream

    #Non-Functional right now
    def getAds( self, link):
        stripurl = re.compile('<ref src="ad.doubleclick.net(.+?)" ').findall(link)
        ads = ['']
        stripurl[0] = 'http://www.cbs.com/thunder/ad.doubleclick.net' + stripurl[0].replace('PARTNER','cbs')
        for url in stripurl:
            url = 'http://www.cbs.com/thunder/ad.doubleclick.net' + stripurl[0].replace('PARTNER','cbs')
            link=common.getHTML(url)
            adsurl = re.compile('src="(.+?)"').findall(link)
            adtrack = re.compile('tp:trackingURLs="0%;(.+?)"').findall(link)
            ads.apend(url)
        return ads
                
        
