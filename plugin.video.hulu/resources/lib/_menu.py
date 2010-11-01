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
        try:
            perpage = common.args.perpage
        except:
            if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                perpage = common.settings['popperpage']
            else:
                perpage = common.settings['perpage']
        xbmcplugin.setPluginCategory( pluginhandle, category=common.args.name )
        xbmcplugin.setPluginFanart(pluginhandle, common.args.fanart)
        self.addMenuItems(perpage,common.args.page)
        if common.args.updatelisting == 'true':
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True, updateListing=True)
        else:
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)

    def getTotalCount( self, itemsurl ):
        if '?' in itemsurl:
            itemsurl += '&dp_id=huludesktop&package_id=2&total=1'
        else:
            itemsurl += '?dp_id=huludesktop&package_id=2&total=1'
        html=common.getFEED(itemsurl)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        items = menuitems=tree.findAll('items')
        for counts in items:
            try:
                return int(counts.find('total_count').string)
            except:
                return 0

      
    def addMenuItems( self, perpage, pagenumber ,url=common.args.url ):
        total_count = self.getTotalCount( url )
        if int(perpage) < int(total_count):
            if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                popular='true'
            else:
                popular='false'
            current_page = int(pagenumber)
            next_page = int(pagenumber)+1
            prev_page = int(pagenumber)-1         
            npage_begin = int(perpage)*current_page + 1
            npage_end = int(perpage)*next_page
            if total_count < npage_end:
                npage_end = total_count
            if npage_begin < total_count:
                next_name = 'Next Page ('+str(npage_begin)+'-'+str(npage_end)+' of '+str(total_count)+')'
                nextthumb=xbmc.translatePath(os.path.join(common.imagepath,"next.png"))
                common.addDirectory(next_name,url,common.args.mode,page=str(next_page),icon=nextthumb,perpage=perpage,popular=popular,updatelisting='true')
            if prev_page > 0:
                ppage_begin = int(perpage)*(prev_page-1)+1
                ppage_end = int(perpage)*prev_page
                prev_name = 'Previous Page ('+str(ppage_begin)+'-'+str(ppage_end)+' of '+str(total_count)+')'
                prevthumb=xbmc.translatePath(os.path.join(common.imagepath,"prev.png"))
                common.addDirectory(prev_name,url,common.args.mode,page=str(prev_page),icon=prevthumb,perpage=perpage,popular=popular,updatelisting='true')

        if '?' in url:
            url += '&dp_id=huludesktop&package_id=2&limit='+perpage+'&page='+pagenumber
        else:
            url += '?dp_id=huludesktop&package_id=2&limit='+perpage+'&page='+pagenumber
        html=common.getFEED(url)
        while html == False:
            html=common.getFEED(url)
            time.sleep(2)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        menuitems=tree.findAll('item')
        del tree
        for item in menuitems:
            display=item.find('display').string.encode('utf-8')
            url='http://m.hulu.com'+item.find('items_url').string
            mode=item.find('cmtype').string
            if display == 'All' and total_count == 1:
                print url
                #common.args.mode = 'All'
                self.addMenuItems(common.settings['allperpage'],common.args.page,url)
                return
            displayname = display
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
                    if common.args.fanart == '' or common.args.fanart == 'http://assets.huluim.com/companies/key_art_hulu.jpg':
                        art = xbmc.translatePath(os.path.join(common.imagepath,"icon.png"))
                        fanart = 'http://assets.huluim.com/companies/key_art_hulu.jpg'
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
                show_name = item.find('show_name').string.encode('utf-8')
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
                #displayname = displayname + ' ('+str(dtotal_count)+')'
                episode_number = dtotal_count
                isVideo = False
            elif mode == 'ShowPage':
                xbmcplugin.setContent(pluginhandle, 'tvshows')
                isVideo = False
            elif common.args.mode == 'ShowPage':
                xbmcplugin.setContent(pluginhandle, 'seasons')
                dtotal_count = self.getTotalCount( url )
                episode_number = dtotal_count
                displayname = displayname + ' ('+str(dtotal_count)+')'
                if dtotal_count == 0:
                    continue
            elif common.args.name == 'Networks' or common.args.name == 'Studios':
                fanart = "http://assets.huluim.com/companies/key_art_"+canonical_name.replace('-','_')+".jpg"
                art = fanart
            elif common.args.mode == 'Menu' and isVideo == False:
                dtotal_count = self.getTotalCount( url )
                if dtotal_count <> 1:
                    displayname = displayname + ' ('+str(dtotal_count)+')'
                elif dtotal_count == 0:
                    continue
            elif isVideo == True:
                pid= item.find('pid').string
                url=pid
                #URL of video
                #url="http://www.hulu.com/watch/"+videoid
                mode = 'TV_play'
                if media_type == 'TV':
                    xbmcplugin.setContent(pluginhandle, 'episodes')
                elif media_type == 'Film':
                    xbmcplugin.setContent(pluginhandle, 'movies')
                    show_name = company_name
                #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
                if season_number <> 0 and episode_number <> 0:
                    if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name or common.args.popular == 'true':
                        #displayname = unicode(show_name+' - '+str(season_number)+'x'+str(episode_number)+' - '+display).encode('utf-8')
                        displayname = show_name+' - '+str(season_number)+'x'+str(episode_number)+' - '+display
                    else:
                        #displayname = unicode(str(season_number)+'x'+str(episode_number)+' - '+display).encode('utf-8')
                        displayname = str(season_number)+'x'+str(episode_number)+' - '+display
                    if 'True' == ishd:
                        displayname += ' (HD)'
            if art == None:
                art = ''
      
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="'+urllib.quote_plus(mode)+'"'
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
            elif int(perpage) < len(menuitems):
                total_items = len(menuitems)
            else:
                total_items = int(total_count)
            if isVideo == False:
                u += '&name="'+urllib.quote_plus(display.replace("'",""))+'"'
                u += '&art="'+urllib.quote_plus(art)+'"'
                u += '&fanart="'+urllib.quote_plus(fanart)+'"'
                u += '&page="1"'
                u += '&popular="false"'
                u += '&updatelisting="false"'
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True,totalItems=total_items)
            elif isVideo == True:
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=total_items)


