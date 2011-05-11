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
        page = common.args.page
        
        url = common.args.url+'?vs=Full%20Episodes'
        data = common.getHTML(url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        try:
            search_elements = tree.find(attrs={'name' : 'searchEl'})['value']
            return_elements = tree.find(attrs={'name' : 'returnEl'})['value']
        except:
            return
        try:
            last_page = tree.find(attrs={'id' : 'pagination0'}).findAll(attrs={'class' : 'vids_pag_off'})[-1].string
            last_page = int(last_page) + 1
        except:
            last_page = 2
        for pageNum in range(1,last_page):
            print pageNum
            values = {'pg' : str(pageNum),
                      'repub' : 'yes',
                      'displayType' : 'twoby',
                      'search_elements' : search_elements,
                      'return_elements' : return_elements,
                      'carouselId' : '0',
                      'vs' : 'Default',
                      'play' : 'true'
                      }
            data = common.getVIDEOS(values)
            self.VIDEOLINKS(data)
        
        #if common.args.updatelist == 'true':
        #    xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True, updateListing=True)
        #else:
        xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)

    def VIDEOLINKS( self, data ):
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        vidfeed=tree.find(attrs={'class' : 'vids_feed'})
        videos = vidfeed.findAll(attrs={'class' : 'floatLeft','style' : True})
        for video in videos:
            print video.prettify()
            vidtitle = video.find(attrs={'class' : 'vidtitle'})
            pid = vidtitle['href'].split('pid=')[1].split('&')[0]
            title = vidtitle.string.encode('utf-8')
            u = sys.argv[0]
            u += '?pid="'+urllib.quote_plus(pid)+'"'
            u += '&mode="Play"'
            item=xbmcgui.ListItem(title)#, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":title
                                                     #"Season":season,
                                                     #"Episode":episode,
                                                     #"Duration":video_length,
                                                     #"TVShowTitle":series,
                                                     })            
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)

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

                        
