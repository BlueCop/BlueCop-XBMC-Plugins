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
import datetime

#from BeautifulSoup import BeautifulStoneSoup

from xml.etree import ElementTree

pluginhandle = int(sys.argv[1])
dp_id = 'hulu'
if (common.settings['enable_plus'] == 'false'):
    package_id = '1'
elif (common.settings['enable_plus'] == 'true'):
    package_id = '2'
    
class Main:
    def __init__( self ):
        try:
            perpage = common.args.perpage
        except:
            if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                perpage = common.settings['popperpage']
            else:
                perpage = common.settings['perpage']
        if 'Subscriptions' == common.args.mode:
            xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.setPluginCategory( pluginhandle, category=common.args.name )
        #xbmcplugin.setPluginFanart(pluginhandle, common.args.fanart)
        self.addMenuItems(perpage,common.args.page)
        if common.args.updatelisting == 'true':
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True, updateListing=True)
        else:
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)

    def getTotalCount( self, itemsurl ):
        if '?' in itemsurl:
            itemsurl += '&dp_id='+dp_id+'&package_id='+package_id+'&total=1'
        else:
            itemsurl += '?dp_id='+dp_id+'&package_id='+package_id+'&total=1'
        xml=common.getFEED(itemsurl)
        tree = ElementTree.XML(xml)
        if tree.findtext('total_count') == "":
            return 0
        else:
            return int(tree.findtext('total_count'))

    def addMenuItems( self, perpage, pagenumber ,url=common.args.url ):
        # Grab xml item list
        orginalUrl = url
        if '?' in url:
            url += '&' 
        else:
            url += '?'
        noCache = False
        if 'Queue' == common.args.mode or 'Subscriptions' == common.args.mode or 'History' == common.args.mode:
            usertoken = common.settings['usertoken']
            url += 'dp_id='+dp_id+'&limit='+perpage+'&package_id='+package_id+'&user_id='+usertoken
            noCache = True
            total_count = 0
        else:
            url += 'dp_id='+dp_id+'&package_id='+package_id+'&limit='+perpage+'&page='+pagenumber
            total_count = self.getTotalCount( orginalUrl )
        if noCache:
            xml = common.getFEED(url)
        else:
            xml=common.getFEED(url)
        while xml == False:
            if noCache:
                xml = common.getFEED(url)
            else:
                xml=common.getFEED(url)
            time.sleep(200)

        # Add Next/Prev Pages
        if int(perpage) < int(total_count):
            if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                popular='true'
            else:
                try:
                    popular = common.args.popular
                except:
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

        tree = ElementTree.XML(xml)
        menuitems = tree.findall('item')        
        del tree
        hasMovies = False
        hasEpisodes = False
        hasTVShows = False
        for item in menuitems:
            display=item.findtext('display').encode('utf-8')
            displayname=display
            url='http://m.hulu.com'+item.findtext('items_url') 
            mode=item.find('app_data').findtext('cmtype')
            
            #Flatten All and Alphabetical
            if display == 'All' and total_count == 1:
                return self.addMenuItems(common.settings['allperpage'],common.args.page,url)
            # Skip unwanted menu items
            elif mode == 'None' or display == 'Add to queue' or display == 'Subscriptions':
                continue
            
            #set Data
            isVideo = False
            if common.args.fanart:
                fanart = common.args.fanart
            else:
                fanart = common.hulu_fanart
            if common.args.art:
                art = common.args.art
            else:
                art = common.hulu_icon

            infoLabels={'Title':display}
            show_id = False
            ishd = False
            data = item.find('data')
            if data:
                #data = data[0]
                canonical_name      = data.findtext('canonical_name')
                show_canonical_name = data.findtext('show_canonical_name')
                #Show Only
                if canonical_name:
                    infoLabels['TVShowTitle'] = data.findtext('name').encode('utf-8')
                    infoLabels['Genre'] = data.findtext('genre')
                    totalEpisodes = data.findtext('full_episodes_count')
                    if totalEpisodes:
                        infoLabels['Episode'] = int(totalEpisodes)
                    totalSeasons = data.findtext('total_seasons_count')
                    parent_id = data.findtext('parent_id')
                    if parent_id:
                        displayname = '- '+displayname
                    art = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                #Video Only
                elif show_canonical_name:
                    isVideo = True
                    canonical_name = show_canonical_name
                    content_id = data.findtext('content_id')
                    video_id = data.findtext('video_id') 
                    media_type = data.findtext('media_type')
                    art = data.findtext('thumbnail_url_16x9_large')
                    infoLabels['TVShowTitle'] = data.findtext('show_name')
                    infoLabels['MPAA'] = data.findtext('content_rating')
                    votes_data = data.findtext('votes_count')
                    seasondata = data.findtext('season_number')
                    if seasondata.isdigit():  
                        infoLabels['Season'] = int(seasondata)
                    else:
                        infoLabels['Season'] = 0
                    episodedata = data.findtext('episode_number')
                    if episodedata.isdigit():
                        infoLabels['Episode'] = int(episodedata)
                    else:
                        infoLabels['Episode'] = 0
                    durationseconds = int(float(data.findtext('duration')))
                    infoLabels['Duration'] =  str(datetime.timedelta(seconds=durationseconds))
                #Both Show and Video
                infoLabels['Plot'] = unicode(data.findtext('description').replace('\n', ' ').replace('\r', ' ')).encode('utf-8')
                premiered =  data.findtext('original_premiere_date')
                if premiered:
                    premiered = premiered.split(' ')[0]
                    infoLabels['Premiered'] = premiered
                    infoLabels['Year'] = int(premiered.split('-')[0])
                rating = data.findtext('rating')
                if rating:
                    if rating.isdigit():
                        infoLabels['Rating'] = float(rating)*2
                else:
                    rating = 0.0
                company_name = data.findtext('company_name')
                infoLabels['Studio'] = company_name
                ishd = data.findtext('has_hd')
                show_id = data.findtext('show_id')
                if canonical_name:
                    fanart = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"

            if mode == 'SeasonMenu':
                xbmcplugin.setContent(pluginhandle, 'seasons')
                dtotal_count = self.getTotalCount( url )
                #displayname = displayname + ' ('+str(dtotal_count)+')'
                episode_number = dtotal_count
                isVideo = False
            elif mode == 'ShowPage':
                xbmcplugin.setContent(pluginhandle, 'tvshows')
                hasTVShows = True
                isVideo = False
            elif common.args.mode == 'ShowPage':
                xbmcplugin.setContent(pluginhandle, 'seasons')
                dtotal_count = self.getTotalCount( url )
                episode_number = dtotal_count
                displayname = displayname + ' ('+str(dtotal_count)+')'
                if dtotal_count == 0:
                    continue
            #Set Networks and Studios fanart
            elif common.args.name == 'Networks' or common.args.name == 'Studios':
                fanart = "http://assets.huluim.com/companies/key_art_"+canonical_name.replace('-','_')+".jpg"
                art = fanart
            #Add Count to Display Name for Non-Show/Episode Lists
            elif common.args.mode == 'Menu' and isVideo == False:
                dtotal_count = self.getTotalCount( url )
                if dtotal_count <> 1:
                    displayname = displayname + ' ('+str(dtotal_count)+')'
                elif dtotal_count == 0:
                    continue
            #Set Final Video Name
            elif isVideo == True:
                url=content_id
                #URL of video
                #url="http://www.hulu.com/watch/"+videoid
                mode = 'TV_play'
                if media_type == 'TV':
                    xbmcplugin.setContent(pluginhandle, 'episodes')
                    hasEpisodes = True
                elif media_type == 'Film':
                    xbmcplugin.setContent(pluginhandle, 'movies')
                    hasMovies = True
                    #infoLabels['TVShowTitle'] = company_name
                #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
                if infoLabels['Season'] <> 0 and infoLabels['Episode'] <> 0:
                    if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name or 'Queue' == common.args.mode or 'History' == common.args.mode or common.args.popular == 'true':
                        displayname = infoLabels['TVShowTitle']+' - '+str(infoLabels['Season'])+'x'+str(infoLabels['Episode'])+' - '+display
                    else:
                        displayname = str(infoLabels['Season'])+'x'+str(infoLabels['Episode'])+' - '+display
            if 'True' == ishd:
                displayname += ' (HD)'
      
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="'+urllib.quote_plus(mode)+'"'
            item=xbmcgui.ListItem(displayname, iconImage=art, thumbnailImage=art)
            item.setInfo( type="Video", infoLabels=infoLabels)
            item.setProperty('fanart_image',fanart)

            #Set total count
            if int(perpage) < int(total_count):
                total_items = int(perpage)
            elif int(perpage) < len(menuitems):
                total_items = len(menuitems)
            else:
                total_items = int(total_count)
                
            cm = []
            if isVideo == False:
                u += '&name="'+urllib.quote_plus(display.replace("'",""))+'"'
                u += '&art="'+urllib.quote_plus(art)+'"'
                u += '&fanart="'+urllib.quote_plus(fanart)+'"'
                u += '&page="1"'
                u += '&popular="false"'
                u += '&updatelisting="false"'
                if common.settings['enable_login']=='true' and common.settings['usertoken']:
                    if 'Subscriptions' == common.args.mode:
                        cm.append( ('Remove Subscription', "XBMC.RunPlugin(%s?mode='removesub'&url=%s)" % ( sys.argv[0], show_id ) ) )
                    elif show_id <> '':
                        cm.append( ('Add to Subscriptions', "XBMC.RunPlugin(%s?mode='addsub'&url=%s)" % ( sys.argv[0], show_id ) ) )
                item.addContextMenuItems( cm ,replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True,totalItems=total_items)
            elif isVideo == True:
                u += '&videoid="'+urllib.quote_plus(video_id)+'"'
                if common.settings['enable_login']=='true' and common.settings['usertoken']:
                    if 'History' == common.args.mode:
                        cm.append( ('Remove from History', "XBMC.RunPlugin(%s?mode='removehistory'&url=%s)" % ( sys.argv[0], video_id ) ) )   
                    if 'Queue' == common.args.mode:
                        cm.append( ('Remove from Queue', "XBMC.RunPlugin(%s?mode='removequeue'&url=%s)" % ( sys.argv[0], video_id ) ) )
                    else:
                        cm.append( ('Add to Queue', "XBMC.RunPlugin(%s?mode='addqueue'&url=%s)" % ( sys.argv[0], video_id ) ) )
                        if show_id <> '':
                            cm.append( ('Add to Subscriptions', "XBMC.RunPlugin(%s?mode='addsub'&url=%s)" % ( sys.argv[0], show_id ) ) )
                cm.append( ('Vote for Video', "XBMC.RunPlugin(%s?mode='vote'&url=%s)" % ( sys.argv[0], video_id ) ) )
                item.addContextMenuItems( cm ,replaceItems=True) 
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=total_items)
        confluence_views = [500,501,502,503,504,508]
        if common.settings['viewenable'] == 'true':
            view=int(common.settings["defaultview"])
            xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")

