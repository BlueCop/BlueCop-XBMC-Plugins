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
print "\n\n entering NBC TV \n\n"

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

        # establish show library context
        showListSegment=re.search('<h3>Show Library</h3>.+?</ul>', content, re.DOTALL).group(0)

        # showURL, title
        shows=re.compile('<li><a href="(http://www.nbc.com/.+?/video/)">(.+?)</a></li>').findall(showListSegment, re.DOTALL)

        for showURL, title in shows:
            title=(title, title + ' (Vintage)')[showURL.find('Vintage_Shows') > 0]  # if vintage, say so
            common.addDirectory(common.cleanNames(title), showURL, 'TV_Seasons_nbc')


    def addSeasonList( self ):

        print "\n\n adding seasons \n\n"

        # get the seasons list from the show page
        content=common.getHTML(common.args.url)

        # establish seasons context; do we have any?
        try:
            seasonsSegment=re.search('<h3>Full Episodes</h3>.+?</ul>', content, re.DOTALL).group(0)
            # seasonURL, name
            seasons=re.compile('<li><a href="(.+?)">(.+?)</a></li>').findall(seasonsSegment, re.DOTALL)
        except:
            seasons=None

        # get the episodes page header
        headerSegment=re.search('<head>.+?</head>', content, re.DOTALL).group(0)
	#print headerSegment
        #fanart=re.compile(".+?background-image: url\(\\'(.+?)\\'", re.DOTALL).findall(headerSegment, re.DOTALL)[0]

        if seasons:
            # are we flat/1 season?
            if common.settings['flat_season'] == 1 or (len(seasons) == 1 and common.settings['flat_season'] == 0):
                common.args.mode='TV_Episodes_nbc'
                for seasonURL, name in seasons:
                    common.args.url=common.NBC_BASE_URL + seasonURL
                    self.addEpisodeList()
            else:
                for seasonURL, name in seasons:
                    #common.addDirectory(name, common.NBC_BASE_URL + seasonURL, 'TV_Episodes_nbc', fanart=common.NBC_BASE_URL + fanart)
                    common.addDirectory(name, common.NBC_BASE_URL + seasonURL, 'TV_Episodes_nbc', 'null')

        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))

        return

        ########## ########## for future work with clips and webisodes

        slider=re.compile('VideoSlider\(.+, ({.+})').findall(content)[0]
        del content

        # get seasons and episodes per season; also determine how many episodes in total
        seasons=re.compile('.+?s(\d+): (\d+)').findall(re.search('episode: {.+?}', slider).group(0))
        episodeCount=re.compile('.+?all: (\d+)').findall(re.search('episode: {.+?}', slider).group(0))[0]

        # URL for the slider call and the showID to plug into it
        sliderURL=re.search('url: \"(.+?)\"', slider).group(1)
        show_id=re.search('show_id: (\d+)', slider).group(1)

        # only add episodes if we have any
        if int(episodeCount) > 0:
            # are we flat/1 season?
            if common.settings['flat_season'] == 1 or (len(seasons) == 1 and common.settings['flat_season'] == 0):
                common.args.mode='TV_Episodes_nbc'
                common.args.url="%s?type=episode&show_id=%s&items_per_page=%s" % (sliderURL, show_id, episodeCount)
                self.addEpisodeList()
            else:
                # one folder per season
                for seasonID, seasonEpisodeCount in seasons:
                    if int(seasonEpisodeCount) > 0:  # some seasons in the list have 0 episodes
                        name="Season %s" % (seasonID)
                        common.args.url="%s?type=episode&show_id=%s&season=%s&items_per_page=%s" % (sliderURL, show_id, seasonID, seasonEpisodeCount)
                        common.addDirectory(name, common.args.url, 'TV_Episodes_nbc')

        # add clips folder if not indicated otherwise
        if not(common.settings['only_full_episodes']):
            clipCount=re.compile('.+?all: (\d+)').findall(re.search('clip: {.+?}', slider).group(0))[0]
            if int(clipCount) > 0:
                common.args.url="%s?type=clip&show_id=%s&items_per_page=%s" % (sliderURL, show_id, clipCount)
                if int(episodeCount) > 0: # only add a clips folder if we have episodes, otherwise go straight to the clips
                    common.addDirectory(xbmc.getLocalizedString(30095), common.args.url, 'TV_Clips')
                else:
                    self.addClipsList()

        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ))


    def addEpisodeList( self ):

        print " \n\n adding episodes \n\n"

        content=common.getHTML(common.args.url)

        # get list of pages of additional episodes, if we have any
        try:
            pagesSegment=re.search('div class="nbcu_pager".+?class="nbcu_pager_last">', content, re.DOTALL).group(0)
            pages=common.unique(re.compile('<a href="(.+?)"').findall(pagesSegment))
            print pages
        except:
            pages=None

        # get episode list per page
        episodeListSegment=re.search('<div class="scet-gallery-content">.+?</div><!-- item list -->', content, re.DOTALL).group(0)

        # title, thumbnail, watchURL, episode, plot
        episodeInfo=re.compile('<li class="list_full_detail_horiz" >.+?href="(.+?)".+?title="(.+?)"><img src="(.+?)".+?<strong>.+?Ep\. (\d+):.+?</div>.+?</li>', re.DOTALL).findall(episodeListSegment, re.DOTALL)
        print episodeInfo

        # season number
        season=re.compile('<h2>Full Episodes.+?(\d+)</span>').findall(episodeListSegment)[0]
        print season

        # add first page worth of episodes
        for watchURL, title, thumbnail, episode in episodeInfo:
            plot = ''
            # build s0xe0y season/episode header if wanted; includes trailing space!
            seasonEpisodeHeader=('', "s%02de%03d " % (int(season), int(episode)))[common.settings['show_epi_labels']]
            # see if we want plots
            plot=('', common.cleanNames(plot))[common.settings['get_episode_plot']]
            common.addDirectory(common.cleanNames(seasonEpisodeHeader + title), watchURL, 'TV_play_nbc', thumbnail, thumbnail, common.args.fanart, plot, 'genre')

        # now loop through rest of episode pages, if any; skip the first page

        # TODO: see if we can consolidate the code from episodeListSegment down,
        # as it duplicates the first page stuff above

        if pages:
            for page in pages[1:]:
                content=common.getHTML(common.NBC_BASE_URL + page)

                # get episode list per page
                episodeListSegment=re.search('<div class="scet-gallery-content">.+?</div><!-- item list -->', content, re.DOTALL).group(0)

                # title, thumbnail, watchURL, episode, plot
                episodeInfo=re.compile('<li class="list_full_detail_horiz" >.+?href="(.+?)".+?title="(.+?)"><img src="(.+?)".+?<strong>.+?Ep\. (\d+):.+?</div>.+?</li>', re.DOTALL).findall(episodeListSegment, re.DOTALL)

                # add each add'l page worth of episodes
                for watchURL, title, thumbnail, episode in episodeInfo:
                    plot = ''
                    # build s0xe0y season/episode header if wanted; includes trailing space!
                    seasonEpisodeHeader=('', "s%02de%03d " % (int(season), int(episode)))[common.settings['show_epi_labels']]
                    # see if we want plots
                    plot=('', common.cleanNames(plot))[common.settings['get_episode_plot']]
                    common.addDirectory(common.cleanNames(seasonEpisodeHeader + title), watchURL, 'TV_play_nbc', thumbnail, thumbnail, common.args.fanart, plot, 'genre')


    def addClipsList( self ):

        print " \n\n adding clips \n\n"

        content=common.getHTML(common.args.url)

        # watchURL, thumbnail, title
        clipInfo=re.compile('<li>.+?<a href="(.+?)".+?<img src="(.+?)".+?alt="(.+?)".+?</li>').findall(content)

        for watchURL, thumbnail, title in clipInfo:
            # see if we want plots
            if common.settings['get_episode_plot']:
                episodeInfoID=re.compile('http://www.hulu.com/watch/(\d+)/').findall(watchURL)[0]
                content=common.getHTML("http://www.hulu.com/videos/info/%s" % (episodeInfoID))
                # only getting description for now; info page also includes:
                #  programming_type, rating, has_captions, episode_number, show_name, title, air_date, content_rating, thumbnail_url, season_number, duration
                plot=repr(re.compile('description: "(.+?)"').findall(content)[0].replace('\n', '\r'))
            else:
                plot=''
            common.addDirectory(common.cleanNames(title), watchURL, 'TV_Clips_play_nbc', thumbnail, thumbnail, common.args.fanart, plot, 'genre')
        del content


#Get SMIL url and play video
def playRTMP():
    vid=re.compile('/(\d+)/').findall(common.args.url)[0]
    smilurl = getsmil(vid)
    rtmpurl = str(getrtmp())
    print rtmpurl
    swfUrl = getswfUrl()
    link = str(common.getHTML(smilurl))
    print link
    match=re.compile('<video src="(.+?)"').findall(link)
    if (common.settings['quality'] == '0'):
            dia = xbmcgui.Dialog()
            ret = dia.select("Quality", ["High","Normal","Exit"])
            if (ret == 2):
                    return
    else:
            ret = None
    for playpath in match:
        playpath = playpath.replace('.flv','')
        if "mp4" in playpath:
            item=xbmcgui.ListItem(common.args.name, iconImage='', thumbnailImage='')
            item.setInfo( type="Video",infoLabels={ "Title": common.args.name})
            if '_1696' in playpath and (xbmcplugin.getSetting(pluginhandle,"quality") == '1' or '_1696' in playpath and (ret == 0)):
                item=xbmcgui.ListItem(common.args.name, iconImage='', thumbnailImage='')
                item.setInfo( type="Video",infoLabels={ "Title": common.args.name})
                rtmpurl += ' playpath=mp4:'+playpath + " swfurl=" + swfUrl + " swfvfy=true"
            elif '_0696' in playpath and (xbmcplugin.getSetting(pluginhandle,"quality") == '2') or '_0696' in playpath and (ret == 1):
                item=xbmcgui.ListItem(common.args.name, iconImage='', thumbnailImage='')
                item.setInfo( type="Video",infoLabels={ "Title": common.args.name})
                rtmpurl += ' playpath=mp4:'+playpath + " swfurl=" + swfUrl + " swfvfy=true"

        else:
            if '_0700' in playpath and (xbmcplugin.getSetting(pluginhandle,"quality") == '1' or '_0700' in playpath and (ret == 0)):
                item=xbmcgui.ListItem(common.args.name, iconImage='', thumbnailImage='')
                item.setInfo( type="Video",infoLabels={ "Title": common.args.name})
                rtmpurl += ' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
            elif '_0500' in playpath and (xbmcplugin.getSetting(pluginhandle,"quality") == '2') or '_0500' in playpath and (ret == 1):
                item=xbmcgui.ListItem(common.args.name, iconImage='', thumbnailImage='')
                item.setInfo( type="Video",infoLabels={ "Title": common.args.name})
                rtmpurl += ' playpath='+playpath + " swfurl=" + swfUrl + " swfvfy=true"
    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(rtmpurl, item)


#Sends over AMF the VID with parameters to get smil from AMF gateway
#figure out last 2 parameters. most likely decompile player.
def getsmil(vid):
    gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
            referer='http://www.nbc.com/assets/video/3-0/swf/NBCVideoApp.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getClipInfo.getClipAll')
    geo  ="US"
    num1 = "632"
    num2 = "-1"
    response = ClipAll_service(vid,geo,num1,num2)
    url = 'http://video.nbcuni.com/' + response['clipurl']
    return url


#get rtmp host and app from amf server congfig. gateway: http://video.nbcuni.com/amfphp/gateway.php Service: getConfigInfo.getConfigAll
def getrtmp():
    #rtmpurl = 'rtmp://cp37307.edgefcs.net:80/ondemand?'
    gw = RemotingService(url='http://video.nbcuni.com/amfphp/gateway.php',
            referer='http://www.nbc.com/assets/video/3-0/swf/NBCVideoApp.swf',
            user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)',
        )
    ClipAll_service = gw.getService('getConfigInfo.getConfigAll')
    #Not sure where this number is coming from need to look further at action script.
    num1 = "17010"
    response = ClipAll_service(num1)
    print response
    for item in response:
        print item
    rtmphost= response['akamaiHostName']
    app = response['akamaiAppName']
    identurl = 'http://'+rtmphost+'/fcs/ident'
    ident = common.getHTML(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    rtmpurl = 'rtmp://'+ip+':1935/'+app+'?_fcs_vhost='+rtmphost
    #rtmpurl = 'rtmp://'+rtmphost+':80/'+app+'?'
    return rtmpurl


#constant right now. not sure how to get this be cause sometimes its another swf module the player loads that access the rtmp server
def getswfUrl():
    swfUrl = "http://www.nbc.com/assets/video/4-0/swf/core/video_player_extension.swf?4.5.5"
    return swfUrl
