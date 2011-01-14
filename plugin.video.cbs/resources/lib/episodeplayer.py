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
            pid = common.args.pid
            #url containing video link
            url = "http://release.theplatform.com/content.select?format=SMIL&Tracking=true&balance=true&MBR=true&pid=" + pid
            link=common.getHTML(url)                 
            if "rtmp://" in link:
                    stripurls = re.compile('<video src="rtmp://(.+?)" system-bitrate=".+?" width="(.+?)" height="(.+?)" profile="(.+?)"').findall(link)
                    #if common.settings['quality'] in stripurls:
                    #   for stripurl, w, h ,profile in stripurls:
                    #       print profile
                    #       print common.settings['quality']
                    #       if common.settings['quality'] == profile:
                    #           cleanurl = stripurl.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').split('<break>')
                    #           finalurl = "rtmp://" + cleanurl[0]
                    #           if ".mp4" in cleanurl[1]:
                    #                   playpath = 'mp4:' + cleanurl[1]
                    #           else:
                    #                   playpath = cleanurl[1].replace('.flv','')
                    #           break
                    #else:
                    hpixels = 0
                    for stripurl, w, h ,profile in stripurls:    
                        pixels = int(w) * int(h)
                        if pixels > hpixels:
                            hpixels = pixels
                            cleanurl = stripurl.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').split('<break>')
                            finalurl = "rtmp://" + cleanurl[0]
                            if ".mp4" in cleanurl[1]:
                                    playpath = 'mp4:' + cleanurl[1]
                            else:
                                    playpath = cleanurl[1].replace('.flv','')

            swfUrl = "http://www.cbs.com/thunder/player/1_0/chromeless/1_5_1/CAN.swf"
            finalurl += ' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
            item = xbmcgui.ListItem(path=finalurl)
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)

                
        
