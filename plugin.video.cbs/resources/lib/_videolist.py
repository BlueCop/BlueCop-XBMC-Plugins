import xbmcplugin
import xbmcgui
import xbmc
import common
import urllib,urllib2
import sys
import re
import os
from BeautifulSoup import BeautifulSoup

pluginhandle = int (sys.argv[1])

class Main:

    def __init__( self ):
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        name = common.args.name
        s = common.args.url
        page = common.args.page
        series = common.args.series
        if s == 'showlist':
            if self.TESTPAGE('all',series) == True:
                common.addDirectory('All Videos'    ,'all'      ,'Videos'   ,series)
            if self.TESTPAGE('latest',series) == True:
                common.addDirectory('Latest Videos' ,'latest'   ,'Videos'   ,series)
            if self.TESTPAGE('fullep',series) == True:
                common.addDirectory('Full Episodes' ,'fullep'   ,'Videos'   ,series)
            if self.TESTPAGE('clips',series) == True:
                common.addDirectory('Clips'         ,'clips'    ,'Videos'   ,series)
        else:
            data = common.getVIDEOS(s,series,page)
            self.ADDPAGES(data, s, series, page)
            self.VIDEOLINKS(data)
        if common.args.updatelist == 'true':
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True, updateListing=True)
        else:
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)

    def TESTPAGE( self, s, series ):
        data = common.getVIDEOS(s,series,'undefined')
        if 'No videos found' in data:
            return False
        else:
            return True
        

    def ADDPAGES( self, data, s, series, page ):
        do_hide     =   re.compile('do_hide\((.+?),(.+?)\);').findall(data)
        page_total  =   re.compile('page-total"\).html\((.+?)\);').findall(data)[0]
        if page == 'undefined':
            pageNum = 0
        else:
            pageNum = int(page)
        pageNext = str(pageNum + 1)
        pageNextName = str(pageNum + 2)
        pagePrev = str(pageNum - 1)
        pagePrevName = str(pageNum)
        if pagePrev == '0':
           pagePrev = 'undefined'
        if do_hide[0][1] == '0':
            pagename = 'Next Page ('+pageNextName+' of '+page_total+')'
            common.addDirectory(pagename,s,'Videos',series,pageNext,'true')
        if do_hide[0][0] == '0':
            pagename = 'Previous Page ('+pagePrevName+' of '+page_total+')'
            common.addDirectory(pagename,s,'Videos',series,pagePrev,'true')

    def VIDEOLINKS( self, data ):        
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        menuitems=tree.findAll(attrs={'class' : 'video'})
        for item in menuitems:
            title  = item.find(attrs={'class' : 'video-title'}).string.encode('utf-8')
            series = item.find(attrs={'class' : 'video-series-title'}).a.string.encode('utf-8')

            
            video_type = item.find(attrs={'class' : 'video-type'}).string.strip().split(' (')[0]
            video_length = item.find(attrs={'class' : 'video-type'}).string.strip().split(' (')[1].replace(')','')

            thumb = item.find(attrs={'class' : 'video-image'}).a.img['src']
            pid = item.find(attrs={'class' : 'video-image'}).a['href'].split('pid=')[1]
            
            try:
                season_episode = item.find(attrs={'class' : 'video-series'}).string.strip().split(':')
                season = int(season_episode[0].strip().replace('Season ',''))
                episode = int(season_episode[1].strip().replace('Ep. ',''))
            except:
                season = 0
                episode = 0

            displayname = title
            if series in title and ' - ' in title:
                if season <> 0 or episode <> 0:
                    if video_type == 'Full Episode':
                        se = ' - '+str(season)+'x'+str(episode)+' - '
                        displayname = title.replace(' - ',se)
                    elif video_type == 'Clip':
                        se = str(season)+'x'+str(episode)
                        displayname += ' ('+video_type+' from '+se+')'

            #if series in title:
            #    title = title.replace(series,'').replace('-',' ').replace(',',' ').replace(':',' ').strip()
            #if season <> 0 or episode <> 0:
            #    if common.args.series == '':
            #        displayname = series+' - '+str(season)+'x'+str(episode)+' - '+title
            #    else:
            #        displayname = str(season)+'x'+str(episode)+' - '+title
            #else:
            #    displayname = series+' - '+title

            u = sys.argv[0]
            u += '?pid="'+urllib.quote_plus(pid)+'"'
            u += '&mode="Play"'
            item=xbmcgui.ListItem(displayname, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":title,
                                                     "Season":season,
                                                     "Episode":episode,
                                                     "Duration":video_length,
                                                     "TVShowTitle":series,
                                                     })            
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)
        #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        return
                        
