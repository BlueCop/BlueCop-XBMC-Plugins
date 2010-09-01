import xbmc
import xbmcplugin
import xbmcgui

import common
import os
import sys
import urllib
import urllib2
import math

from BeautifulSoup import BeautifulStoneSoup

pluginhandle = int(sys.argv[1])

class Main:
    def __init__( self ):
            if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                perpage = '100'
            else:
                perpage = common.settings['perpage']
            self.addMenuItems(perpage)
            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

    def getTotalCount( self, url ):
        if '?' in url:
            itemsurl = 'http://m.hulu.com'+url+'&dp_id=huludesktop&package_id=2&total=1'
        else:
            itemsurl = 'http://m.hulu.com'+url+'?dp_id=huludesktop&package_id=2&total=1'
        html=common.getFEED(itemsurl)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        items = menuitems=tree.findAll('items')
        for counts in items:
            try:
                return int(counts.find('total_count').string)
            except:
                return 0
                
    def addMenuItems( self, perpage, url=common.args.url ):
        total_count = self.getTotalCount( url )
        if '?' in url:
            url = 'http://m.hulu.com'+url+'&dp_id=huludesktop&package_id=2&limit='+perpage+'&page=1'
        else:
            url = 'http://m.hulu.com'+url+'?dp_id=huludesktop&package_id=2&limit='+perpage+'&page=1'
        html=common.getFEED(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        menuitems=tree.findAll('item')
        del tree
        for item in menuitems:
            display=unicode(common.cleanNames(item.find('display').string)).encode('utf-8')
            url=item.find('items_url').string
            if display == 'All' and total_count == 1:
                print url
                common.args.mode = 'All'
                self.addMenuItems('2000',url)
                return
            displayname = display
            mode=item.find('cmtype').string
            if mode == 'None' or display == 'Add to queue' or display == 'Subscriptions' or display == 'Recommended':
                continue
            try:
                if 'True' == item.find('is_plus_web_only').string:
                    isPlus = True
                    if (common.settings['enable_plus'] == 'false'):
                        continue
            except:
                isPlus = False
            try:
                canonical_name = item.find('canonical_name').string
                art = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                fanart = art
                isVideo = False
            except:
                try:
                    canonical_name = item.find('show_canonical_name').string
                    fanart = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                    isVideo = True
                except:
                    if common.args.fanart == '':
                        art = xbmc.translatePath(os.path.join(common.imagepath,"icon.png"))
                    else:
                        art = common.args.fanart
                    fanart = common.args.fanart
            try:
                thumbnail_url_16x9_large = item.find('thumbnail_url_16x9_large').string
                art = thumbnail_url_16x9_large
                isVideo = True
            except:
                isVideo = False
            try:
                description = unicode(common.cleanNames(item.find('description').string.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
            except:
                description = ''
            try:
                genre = item.find('genre').string
            except:
                genre = ''
            try:
                season_number = int(item.find('season_number').string)
            except:
                season_number = 0
            try:
                episode_number = int(item.find('episode_number').string)
            except:
                episode_number = 0
            try:
                show_name = item.find('show_name').string
            except:
                show_name = ''                 
            try:
                duration = str(math.ceil(float(item.find('duration').string) / 60))
            except:
                duration = ''
            try:
                premiered = item.find('original_premiere_date').string.replace(' 00:00:00','')
                year = int(premiered.split('-')[0])
            except:
                premiered = ''
                year = 0
            try:
                company_name = item.find('company_name').string
            except:
                company_name = ''
            try:
                rating = float(item.find('rating').string)*2
                votes = item.find('votes_count').string
            except:
                rating = 0
                votes = ''
            try:
                mpaa = item.find('content_rating').string
            except:
                mpaa = ''
            try:
                ishd = item.find('has_hd').string
                if 'True' == ishd:
                    resolution = '720'
                else:
                    resolution = '480'
            except:
                ishd = 'False' 
                resolution = ''   
            try:
                media_type = item.find('media_type').string
            except:
                media_type = False         
            try:
                videoid = item.find('video_id').string
                isVideo = True
            except:
                isVideo = False
            if mode == 'SeasonMenu':
                xbmcplugin.setContent(pluginhandle, 'seasons')
                dtotal_count = self.getTotalCount( url )
                displayname = displayname + ' ('+str(dtotal_count)+')'
                isVideo = False
            elif common.args.mode == 'ShowPage':
                dtotal_count = self.getTotalCount( url )
                displayname = displayname + ' ('+str(dtotal_count)+')'
                if dtotal_count == 0:
                    continue
            elif common.args.mode == 'Menu' and isVideo == False:
                dtotal_count = self.getTotalCount( url )
                if dtotal_count <> 1:
                    displayname = displayname + ' ('+str(dtotal_count)+')'
                elif dtotal_count == 0:
                    continue
            elif isVideo == True:
                pid= item.find('pid').string
                url=pid
                #url="http://www.hulu.com/watch/"+videoid
                mode = 'TV_play'
                if media_type == 'TV':
                    xbmcplugin.setContent(pluginhandle, 'episodes')
                elif media_type == 'Film':
                    xbmcplugin.setContent(pluginhandle, 'movies')
                    show_name = company_name
                #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
                if season_number <> 0 and episode_number <> 0:
                    if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                        displayname = unicode(show_name+' - '+str(season_number)+'x'+str(episode_number)+' - '+display).encode('utf-8')
                    else:
                        displayname = unicode(str(season_number)+'x'+str(episode_number)+' - '+display).encode('utf-8')
                    if 'True' == ishd:
                        displayname += ' (HD)'
            if art == None:
                art = ''
      
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(common.cleanNames(url))+'"'
            u += '&mode="'+urllib.quote_plus(common.cleanNames(mode))+'"'
            u += '&name="'+urllib.quote_plus(common.cleanNames(display))+'"'
            u += '&plot="'+urllib.quote_plus(common.cleanNames(description))+'"'
            u += '&genre="'+urllib.quote_plus(common.cleanNames(genre))+'"'
            u += '&season="'+urllib.quote_plus(common.cleanNames(str(season_number)))+'"'
            u += '&episode="'+urllib.quote_plus(common.cleanNames(str(episode_number)))+'"'
            u += '&tvshowtitle="'+urllib.quote_plus(common.cleanNames(show_name))+'"'
            u += '&premiered="'+urllib.quote_plus(common.cleanNames(premiered))+'"'
            u += '&art="'+urllib.quote_plus(common.cleanNames(art))+'"'
            u += '&fanart="'+urllib.quote_plus(common.cleanNames(fanart))+'"'
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
            if isVideo == False:
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True,totalItems=total_items)
            elif isVideo == True:
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=total_items)


