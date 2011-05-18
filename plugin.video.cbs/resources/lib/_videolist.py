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
        
        data = common.getHTML(common.args.url)
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        if page == 'optionlist':
            try:
                options = tree.find(attrs={'id' : 'secondary-show-nav-wrapper'})
                options = options.findAll('a')
                for option in options:
                    name = option.string.encode('utf-8')
                    url = common.BASE + option['href']
                    common.addDirectory(name,url,'Videos','1')
            except:
                print 'CBS: secondary-show-nav-wrapper failed'
                print 'CBS: trying vid_module'
                try:
                    options = tree.findAll(attrs={'class' : 'vid_module'})
                    for option in options:
                        moduleid = option['id']
                        name = option.find(attrs={'class' : 'hdr'}).string
                        common.addDirectory(name,common.args.url,'Videos',moduleid)                                        
                except:
                    print 'CBS: vid_module failed'
        elif page == '1':
            print 'CBS: trying vid_module'
            try:
                options = tree.findAll(attrs={'class' : 'vid_module'})
                if len(options) == 1:
                    self.PAGES(tree)
                else:
                    for option in options:
                        moduleid = option['id']
                        name = option.find(attrs={'class' : 'hdr'}).string
                        common.addDirectory(name,common.args.url,'Videos',moduleid)                                        
            except:
                self.PAGES(tree)
        elif 'vid_module' in page:
            vid_module = tree.find(attrs={'id' : page})
            self.PAGES(vid_module)
            
        if common.args.updatelist == 'true':
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True, updateListing=True)
        else:
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)
            

    def PAGES( self, tree ):
            try:
                search_elements = tree.find(attrs={'name' : 'searchEl'})['value']
                return_elements = tree.find(attrs={'name' : 'returnEl'})['value']
            except:
                print 'CBS: search and return elements failed'
            try:
                last_page = tree.find(attrs={'id' : 'pagination0'}).findAll(attrs={'class' : 'vids_pag_off'})[-1].string
                last_page = int(last_page) + 1
            except:
                print 'CBS: last page failed reverting to default'
                last_page = 2
            for pageNum in range(1,last_page):
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

    def VIDEOLINKS( self, data ):
        tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        vidfeed=tree.find(attrs={'class' : 'vids_feed'})
        videos = vidfeed.findAll(attrs={'class' : 'floatLeft','style' : True})
        for video in videos:
            thumb = video.find('img')['src']
            vidtitle = video.find(attrs={'class' : 'vidtitle'})
            pid = vidtitle['href'].split('pid=')[1].split('&')[0]
            displaytitle = vidtitle.string.encode('utf-8')
            try:
                title = displaytitle.split('-')[1].strip()
                series = displaytitle.split('-')[0].strip()
            except:
                print 'title/series metadata failure'
                title = displaytitle
                series = ''

            metadata = video.find(attrs={'class' : 'season_episode'}).renderContents()
            try:
                duration = metadata.split('(')[1].replace(')','')
            except:
                print 'duration metadata failure'
                duration = ''
            try:
                aired = metadata.split('<')[0].split(':')[1].strip()
            except:
                print 'air date metadata failure'
                aired = ''
                
            u = sys.argv[0]
            u += '?pid="'+urllib.quote_plus(pid)+'"'
            u += '&mode="Play"'
            item=xbmcgui.ListItem(displaytitle, iconImage=thumb, thumbnailImage=thumb)
            item.setInfo( type="Video", infoLabels={ "Title":title,
                                                     #"Season":season,
                                                     #"Episode":episode,
                                                     "premiered":aired,
                                                     "Duration":duration,
                                                     "TVShowTitle":series
                                                     }) 
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False)

                        
