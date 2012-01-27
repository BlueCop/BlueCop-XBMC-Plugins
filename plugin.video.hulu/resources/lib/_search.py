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
dp_id = 'hulu'
if (common.settings['enable_plus'] == 'false'):
    package_id = '1'
elif (common.settings['enable_plus'] == 'true'):
    package_id = '2'
    
class Main:
    def __init__( self ):
        perpage = common.settings['searchperpage']
        if common.args.updatelisting == 'true':
            search = common.args.url
            self.addMenuItems(perpage,common.args.page,search,'0')
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)
        else:
            keyb = xbmc.Keyboard('', 'Search')
            keyb.doModal()
            if (keyb.isConfirmed()):
                search = urllib.quote_plus(keyb.getText())
                self.addMenuItems(perpage,common.args.page,search,'1')
                xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)
      
    def addMenuItems( self, perpage, pagenumber , search, huluonly ):
        url = 'http://m.hulu.com/search?items_per_page='+perpage+'&hulu_only='+huluonly+'&dp_identifier='+dp_id+'&package_id='+package_id+'&query='+search
        html=common.getFEED(url)
        while html == False:
            html=common.getFEED(url)
            time.sleep(2)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        total_count= int(tree('results')[0]('count')[0].string)
        if huluonly == '1' and total_count == 0:
            self.addMenuItems(perpage,pagenumber,search,'0')
            return
        elif huluonly == '1':
            searchicon = xbmc.translatePath(os.path.join(common.imagepath,"search_icon.png"))
            common.addDirectory('Search Off Hulu',search,'Search', thumb=searchicon, icon=searchicon, updatelisting='true')
        menuitems=tree.findAll('video')
        del tree
        for item in menuitems:
            display=item('title')[0].string.encode('utf-8')
            content_id = item('content-id')
            url = item('url')
            if content_id:
                url = content_id[0].string
                offsite= 'false'
                source_site= 'Hulu'
            elif url:
                url= url[0].string
                offsite= item('offsite')[0].string
                source_site= item('source-site')[0].string.encode('utf-8')
            else:
                return
            mode = 'TV_play'
            displayname = display
            description = ''
            full_description = ''
            show_name = ''
            company_name = ''
            duration = ''
            genre = ''
            parent_id = None
            season_number = 0
            episode_number = 0
            premiered = ''
            year = 0
            rating = 0.0
            votes = ''
            mpaa = ''
            media_type = False

            canonical_name = item.find('show').find('canonical-name').string
            content_id = item('content-id')[0].string
            media_type = item('media-type')[0].string
            art = item('thumbnail-url')[0].string
            show_name = item('show')[0]('name')[0].string.encode('utf-8')#item('show-name')[0].string.encode('utf-8')
            mpaa = item('content-rating')[0].string
            votes_data = item('votes-count')
            if votes_data[0].string:
                votes = votes_data[0].string
            premiered_data = item('original-premiere-date')
            if premiered_data[0].string:
                premiered = premiered_data[0].string.replace('T00:00:00Z','')
                year = int(premiered.split('-')[0])
            season_number_data = item('season-number')
            if season_number_data[0].string:
                season_number = int(season_number_data[0].string)
            episode_number_data = item('episode-number')
            if episode_number_data[0].string:
                episode_number = int(episode_number_data[0].string)
            duration_data = item('duration')
            if duration_data[0].string:
                duration = float(duration_data[0].string)
                hour = int(math.floor(duration / 60 / 60))
                minute = int(math.floor((duration - (60*60*hour))/ 60))
                second = int(duration - (60*minute)- (60*60*hour))
                if len(str(second)) == 1:
                    second = '0'+str(second)
                if len(str(minute)) == 1:
                    minute = '0'+str(minute)
                if hour == 0:
                    duration = str(minute)+':'+str(second)
                elif len(str(hour)) == 1:
                    duration = '0'+str(hour)+':'+str(minute)+':'+str(second)
                else:
                    duration = str(hour)+':'+str(minute)+':'+str(second)
            full_description_data = item('full-description')
            if full_description_data:
                if full_description_data[0].string:
                    full_description = unicode(common.cleanNames(full_description_data[0].string.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
            description_data = item('description')
            if description_data:
                if description_data[0].string:
                    if full_description <> '':
                        description = unicode(common.cleanNames(description_data[0].string.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
                    else:
                        full_description = unicode(common.cleanNames(description_data[0].string.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
            rating_data = item('rating')
            if rating_data:
                if rating_data[0].string:
                    rating = float(rating_data[0].string)*2
            company_name_data = item('company-name')
            if company_name_data:
                company_name = company_name_data[0].string
            ishd_data = item('has-hd')
            if ishd_data:
                ishd = ishd_data[0].string
            if canonical_name:
                fanart = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                
            if season_number <> 0 and episode_number <> 0:
                displayname = show_name+' - '+str(season_number)+'x'+str(episode_number)+' - '+display
            elif show_name <> '' and show_name not in display:
                displayname = show_name+' - '+display
                
            if media_type == 'TV':
                xbmcplugin.setContent(pluginhandle, 'episodes')
            elif media_type == 'Film':
                xbmcplugin.setContent(pluginhandle, 'movies')


            if 'True' == ishd:
                displayname += ' (HD)'
            if 'true' == offsite:
                displayname += ' ('+source_site+')'
                mode = 'TV_playoffsite'
                

            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="'+urllib.quote_plus(mode)+'"'
            #u += '&name="'+urllib.quote_plus(display)+'"'
            u += '&page="1"'
            u += '&art="'+urllib.quote_plus(art)+'"'
            u += '&fanart="'+urllib.quote_plus(fanart)+'"'
            u += '&sourcesite="'+urllib.quote_plus(source_site)+'"'
            u += '&popular="false"'
            u += '&updatelisting="false"'
            item=xbmcgui.ListItem(displayname, iconImage=art, thumbnailImage=art)
            item.setInfo( type="Video", infoLabels={ "Title":display,
                                                     "Plot":full_description,
                                                     "PlotOutline":description,
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
                                                     "Votes":votes
                                                     })
            item.setProperty('fanart_image',fanart)
            if int(perpage) < int(total_count):
                total_items = int(perpage)
            else:
                total_items = int(total_count)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=total_items)


