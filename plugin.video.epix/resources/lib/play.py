#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import urllib
import demjson
from BeautifulSoup import BeautifulStoneSoup
import xbmcplugin
import xbmc
import xbmcgui
import resources.lib.common as common

pluginhandle = common.pluginhandle

def PLAYVIDEO():
    #orgin = 'http://dish.epixhd.com/epx/ajax/user/originstatus/'
    #print common.getURL(orgin,useCookie=True)
    #pageurl = 'http://www.epixhd.com/epx/ajax/theater/soloplayer'+common.args.url
    #print common.getURL(pageurl,useCookie=True)
    smilurl = 'http://www.epixhd.com/epx/smil'+common.args.url+'smil.xml'
    data = common.getURL(smilurl,useCookie=True)
    tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    quality = [0,3000000,2200000,1700000,1200000,900000,500000]
    lbitrate = quality[int(common.addon.getSetting("bitrate"))]
    mbitrate = 0
    streams = []
    for item in tree.find('mbrstream').findAll('video'):
        url = item['src']
        bitrate = int(item['system-bitrate'])
        if lbitrate == 0:
            streams.append([bitrate/1000,url])
        elif bitrate >= mbitrate and bitrate <= lbitrate:
            mbitrate = bitrate
            rtmpdata = url
    if lbitrate == 0:        
        quality=xbmcgui.Dialog().select('Please select a quality level:', [str(stream[0])+'kbps' for stream in streams])
        if quality!=-1:
            rtmpdata = streams[quality][1]
        else:
            return

    authurl = 'http://www.epixhd.com/epx/ajax/theater/getToken/?url=/'
    auth = common.getURL(authurl,useCookie=True)  
    rtmpsplit = rtmpdata.split('?')
    parameters = rtmpsplit[1]+'&auth='+auth
    filename = 'mp4:'+rtmpsplit[0].split('mp4:')[1]
    rtmpbase = rtmpdata.split(filename)[0]
        
    finalUrl = rtmpbase+'?'+parameters
    finalUrl += ' playpath='+filename
    finalUrl += ' swfurl=http://www.epixhd.com/Epix.v2.0.37.1.swf swfvfy=true'
    
    item = xbmcgui.ListItem(path=finalUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)