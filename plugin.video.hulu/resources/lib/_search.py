import xbmc
import xbmcplugin
import xbmcgui

import common
import os
import sys
import urllib
import urllib2
import math
import time

from BeautifulSoup import BeautifulStoneSoup

pluginhandle = int(sys.argv[1])

class Main:
    def __init__( self ):
        perpage = common.settings['searchperpage']
        keyb = xbmc.Keyboard('', 'Search')
        keyb.doModal()
        if (keyb.isConfirmed()):
            search = urllib.quote_plus(keyb.getText())
            self.addMenuItems(perpage,common.args.page,search)
            if common.args.updatelisting == 'true':
                xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True, updateListing=True)
            else:
                xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)
      
    def addMenuItems( self, perpage, pagenumber ,url ):
        url = 'http://m.hulu.com/search?items_per_page='+perpage+'&hulu_only=1&dp_identifier=huludesktop&package_id=2&query='+url
        html=common.getFEED(url)
        while html == False:
            html=common.getFEED(url)
            time.sleep(2)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        menuitems=tree.findAll('video')
        total_count= int(tree.find('count').string)
        del tree
        for item in menuitems:
            display=unicode(common.cleanNames(item.find('title').string)).encode('utf-8')
            url= item.find('pid').string
            mode = 'TV_play'
            displayname = display
            try:
                if 'true' == item.find('has-plus-web').string:
                    isPlus = True
                    if (common.settings['enable_plus'] == 'false'):
                        continue
            except:
                isPlus = False
            try:
                canonical_name = item.find('show').find('canonical-name').string
                fanart = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
            except:
                fanart = common.args.fanart
            try:
                thumbnail_url_16x9_large = item.find('thumbnail-url').string
                art = thumbnail_url_16x9_large
            except:
                isVideo = True
            try:
                description = unicode(common.cleanNames(item.find('description').string.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
            except:
                description = ''
            try:
                genre = item.find('genre').string
            except:
                genre = ''
            try:
                season_number = int(item.find('season-number').string)
            except:
                season_number = 0
            try:
                episode_number = int(item.find('episode-number').string)
            except:
                episode_number = 0
            try:
                show_name = item.find('name').string
            except:
                show_name = ''                 
            try:
                duration = float(item.find('duration').string)
                hour = int(math.floor(duration / 60 / 60))
                minute = int(math.floor((duration - (60*60*hour))/ 60))
                second = int(duration - (60*minute)- (60*60*hour))
                if hour == 0:
                    duration = str(minute)+':'+str(second)
                else:
                    duration = str(hour)+':'+str(minute)+':'+str(second)
            except:
                duration = ''
            try:
                premiered = item.find('original-premiere-date').string.replace('T00:00:00Z','')
                year = int(premiered.split('-')[0])
            except:
                premiered = ''
                year = 0
            try:
                company_name = item.find('company-name').string
            except:
                company_name = ''
            try:
                rating = float(item.find('rating').string)*2
                votes = item.find('votes_count').string
            except:
                rating = 0
                votes = ''
            try:
                mpaa = item.find('content-rating').string
            except:
                mpaa = ''
            try:
                ishd = item.find('has-hd').string
                if 'True' == ishd:
                    resolution = '720'
                else:
                    resolution = '480'
            except:
                ishd = 'False' 
                resolution = ''   
            try:
                media_type = item.find('media-type').string
            except:
                media_type = False
            if media_type == 'TV':
                xbmcplugin.setContent(pluginhandle, 'episodes')
            elif media_type == 'Film':
                xbmcplugin.setContent(pluginhandle, 'movies')
                show_name = company_name
            if season_number <> 0 and episode_number <> 0:
                displayname = show_name+' - '+str(season_number)+'x'+str(episode_number)+' - '+display
            else:
                displayname = show_name+' - '+display
            if 'True' == ishd:
                displayname += ' (HD)'
            if art == None:
                art = ''
      
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="'+urllib.quote_plus(mode)+'"'
            u += '&name="'+urllib.quote_plus(display)+'"'
            u += '&page="1"'
            u += '&art="'+urllib.quote_plus(art)+'"'
            u += '&fanart="'+urllib.quote_plus(fanart)+'"'
            u += '&popular="false"'
            u += '&updatelisting="false"'
            item=xbmcgui.ListItem(displayname, iconImage=art, thumbnailImage=art)
            item.setInfo( type="Video", infoLabels={ "Title":display,
                                                     "Plot":description,
                                                     "Genre":genre,
                                                     "Season":season_number,
                                                     "Episode":episode_number,
                                                     "Duration":duration,
                                                     "premiered":premiered,
                                                     "TVShowTitle":show_name,
                                                     "Studio":company_name,
                                                     "Year":year,
                                                     "MPAA":mpaa,
                                                     "Rating":rating,
                                                     "Votes":votes,
                                                     "VideoResolution":resolution,
                                                     "VideoCodec":"h264",
                                                     "AudioCodec":"aac"
                                                     })
            item.setProperty('fanart_image',fanart)
            if int(perpage) < int(total_count):
                total_items = int(perpage)
            else:
                total_items = int(total_count)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=total_items)


