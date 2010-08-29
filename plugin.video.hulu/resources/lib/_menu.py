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
            self.addMenuItems()
            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )


    def addMenuItems( self ):
        if '?' in common.args.url:
            url = 'http://m.hulu.com'+common.args.url+'&dp_id=huludesktop&package_id=2&limit='+common.settings['perpage']+'&page=1'
        else:
            url = 'http://m.hulu.com'+common.args.url+'?dp_id=huludesktop&package_id=2&limit='+common.settings['perpage']+'&page=1'
        html=common.getFEED(url)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        menuitems=tree.findAll('item')
        for item in menuitems:
            display=unicode(common.cleanNames(item.find('display').string)).encode('utf-8')
            displayname = display
            url=item.find('items_url').string
            mode=item.find('cmtype').string
            if mode == 'None' or display == 'Add to queue' or display == 'Subscriptions' or display == 'Recommended':
                continue
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
                isVideo = False
            elif isVideo == True:
                url="http://www.hulu.com/watch/"+videoid
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
            u += '&art="'+urllib.quote_plus(art)+'"'
            u += '&fanart="'+urllib.quote_plus(fanart)+'"'
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
                                                     "Rating":rating,
                                                     "Votes":votes,
                                                     "mpaa":mpaa})
            item.setProperty('fanart_image',fanart)
            if isVideo == False:
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True)
            elif isVideo == True:
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)
