import xbmcplugin
import xbmcgui
import xbmc

import common

import sys
import re

import urllib, urllib2
import os

from elementtree.ElementTree import *
from pyamf.remoting.client import RemotingService

pluginhandle = int (sys.argv[1])
print "\n\n entering SciFi TV \n\n"

class Main:

    def __init__( self ):
         
        if common.args.mode.startswith('TV') and common.settings['flat_tv_cats']:
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            self.addShowsList()
            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))
        elif common.args.mode.startswith('TV_Seasons'):
            self.addSeasonList()
        elif common.args.mode.startswith('TV_Episodes'):
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            self.addEpisodeList()
            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))
        elif common.args.mode.startswith('TV_Clips'):
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            self.addClipsList()
        else:
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            self.addShowsList()
            if (common.settings["flat_channels"]): return
            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))


    def addShowsList( self ):

        print "\n\n adding shows \n\n"

        content=common.getHTML(common.args.url)
        
        # title, thumb, id, fanart
        shows=re.compile('<series>.+?<name>(.+?)</name>.+?<thumbnailUrl>(.+?)</thumbnailUrl>.+?<id>(\d+)</id>.+?<backgroundUrl>(.+?)</backgroundUrl>.+?</series>', re.DOTALL).findall(content, re.DOTALL)

        for title, thumb, id, fanart in shows:
            showURL="http://video.scifi.com/player/feeds/?level=%s&type=placement&showall=1" % (id)
            common.addDirectory(common.cleanNames(title), showURL, 'TV_Episodes_scifi', thumb=common.SCIFI_BASE_URL + thumb, fanart=common.SCIFI_BASE_URL + fanart)


    def addSeasonList( self ):

        print "\n\n there are no seasons on scifi -- how did we get here? \n\n"
        

    def addEpisodeList( self ):

        print " \n\n adding episodes \n\n"
        
        content=common.getHTML(common.args.url)

        # title, watchURL, plot, thumbnail
        episodeInfo=re.compile('<item>.+?<title>.+?CDATA\[(.+?)\].+?<link>(.+?id=\d+).+?</link>.+?<description>.+?CDATA\[(.+?)\].+?thumbnail.+?url="(.+?)"', re.DOTALL).findall(content, re.DOTALL)
        
        # add episodes
        for title, watchURL, plot, thumbnail in episodeInfo:
            # see if we want plots
            plot=('', common.cleanNames(plot))[common.settings['get_episode_plot']]
            common.addDirectory(common.cleanNames(title), watchURL, 'TV_play_scifi', thumbnail, thumbnail, common.args.fanart, plot, 'genre')


    def addClipsList( self ):
        
        print "\n\n there are no clips on scifi -- how did we get here? \n\n"


#Get SMIL url and play video
def playRTMP():
    
    vid=re.compile('id=(\d+)').findall(common.args.url)[0]
    
    smilurl = getsmil(vid)
    rtmpurl = str(getrtmp())
    swfUrl = getswfUrl()
    link = str(common.getHTML(smilurl))
    
    match=re.compile('<video src="(.+?)"').findall(link)
    if (common.settings['quality'] == '0'):
            dia = xbmcgui.Dialog()
            ret = dia.select(xbmc.getLocalizedString(30004), [xbmc.getLocalizedString(30016),xbmc.getLocalizedString(30017),xbmc.getLocalizedString(30018)])
            if (ret == 2):
                    return
    else:        
            ret = None
    for playpath in match:
        playpath = playpath.replace('.flv','')
        if '_0700' in playpath and (xbmcplugin.getSetting(pluginhandle,"quality") == '1' or '_0700' in playpath and (ret == 0)):
            item=xbmcgui.ListItem(common.args.name, iconImage='', thumbnailImage='')
            item.setInfo( type="Video",infoLabels={ "Title": common.args.name})
            item.setProperty("SWFPlayer", swfUrl)
            item.setProperty("PlayPath", playpath)
        elif '_0500' in playpath and (xbmcplugin.getSetting(pluginhandle,"quality") == '2') or '_0500' in playpath and (ret == 1):
            item=xbmcgui.ListItem(common.args.name, iconImage='', thumbnailImage='')
            item.setInfo( type="Video",infoLabels={ "Title": common.args.name})
            item.setProperty("SWFPlayer", swfUrl)
            item.setProperty("PlayPath", playpath)
    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(rtmpurl, item)


#get smil url from amf server. gateway: http://video.nbcuni.com/amfphp/gateway.php Service: getClipInfo.getClipAll
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


#get rtmp host and app from amf server congfig. gateway: http://video.nbcuni.com/amfphp/gateway.php Service: getConfigInfo.getConfigAll
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
