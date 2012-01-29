import xbmc
import xbmcplugin
import xbmcgui

import common
import sys
import urllib
import datetime

try:
    from xml.etree import ElementTree
except:
    from elementtree import ElementTree

pluginhandle = int(sys.argv[1])
dp_id = 'hulu'
if (common.settings['enable_plus'] == 'false'):
    package_id = '1'
elif (common.settings['enable_plus'] == 'true'):
    package_id = '2'
    
class Main:
    def __init__( self ):
        perpage = common.settings['searchperpage']
        keyb = xbmc.Keyboard('', 'Search')
        keyb.doModal()
        if (keyb.isConfirmed()):
            search = urllib.quote_plus(keyb.getText())
            self.addMenuItems(perpage,common.args.page,search,'1')
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)
            confluence_views = [500,501,502,503,504,508]
            if common.settings['viewenable'] == 'true':
                view=int(common.settings["defaultview"])
                xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[view])+")")
  
    def addMenuItems( self, perpage, pagenumber , search, huluonly ):
        url = 'http://m.hulu.com/search?items_per_page='+perpage+'&hulu_only='+huluonly+'&dp_identifier='+dp_id+'&package_id='+package_id+'&query='+search
        xml=common.getFEED(url)
        while xml == False:
            xml=common.getFEED(url)
            xbmc.sleep(400)
        tree = ElementTree.XML(xml)
        total_count= int(tree.findtext('count'))
        menuitems = tree.find('videos').findall('video')
        del tree
        for item in menuitems:
            infoLabels={}
            infoLabels['Title']=item.findtext('title').encode('utf-8')
            infoLabels['Genre'] = item.findtext('genre')
            infoLabels['TVShowTitle'] = item.find('show').findtext('name').encode('utf-8')
            infoLabels['MPAA'] = item.findtext('content-rating')
            infoLabels['Votes'] = item.findtext('votes-count')
            infoLabels['Premiered'] = item.findtext('original-premiere-date').replace('T00:00:00Z','')
            if infoLabels['Premiered'] <> '':
                infoLabels['Year'] = int(infoLabels['Premiered'].split('-')[0])
            season = item.findtext('season-number')
            if season <> '':
                infoLabels['Season'] = int(season)
            else:
                infoLabels['Season'] = 0
            episode = item.findtext('episode-number')
            if episode <> '':
                infoLabels['Episode'] = int(episode)
            else:
                infoLabels['Episode'] = 0
            durationseconds = int(float(item.findtext('duration')))
            infoLabels['Duration'] =  str(datetime.timedelta(seconds=durationseconds))
            infoLabels['Rating'] = float(item.findtext('rating'))*2
            full_description = item.findtext('full-description')
            description = item.findtext('description')
            if full_description <> '':
                infoLabels['Plot'] = full_description.replace('\n', ' ').replace('\r', ' ').encode('utf-8')
            elif description <> '':
                infoLabels['Plot']  = description.replace('\n', ' ').replace('\r', ' ').encode('utf-8')
            
            company_name = item.findtext('company-name')
            content_id = item.findtext('content-id')
            video_id = item.findtext('id')
            show_id = item.find('show').findtext('id')

            art = item.findtext('thumbnail-url')
            canonical_name = item.find('show').findtext('canonical-name')
            if canonical_name <> '' and canonical_name <> None:
                fanart = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
            else:
                fanart = common.hulu_fanart
            
            if infoLabels['Season'] <> 0 and infoLabels['Episode'] <> 0:
                displayname = infoLabels['TVShowTitle']+' - '+str(infoLabels['Season'])+'x'+str(infoLabels['Episode'])+' - '+infoLabels['Title']
            elif infoLabels['TVShowTitle'] <> '' and infoLabels['TVShowTitle'] not in infoLabels['Title']:
                displayname = infoLabels['TVShowTitle']+' - '+infoLabels['Title']
            else:
                displayname = infoLabels['Title']
                
            ishd = item.findtext('has-hd')
            if 'True' == ishd:
                displayname += ' (HD)'
            hascaptions = item.findtext('has-captions')
                
            
            media_type = item.findtext('media-type')
            if media_type == 'TV':
                xbmcplugin.setContent(pluginhandle, 'episodes')
            elif media_type == 'Film':
                xbmcplugin.setContent(pluginhandle, 'movies')

            mode = 'TV_play'
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(content_id)+'"'
            u += '&mode="'+urllib.quote_plus(mode)+'"'
            u += '&videoid="'+urllib.quote_plus(video_id)+'"'
            item=xbmcgui.ListItem(displayname, iconImage=art, thumbnailImage=art)
            item.setInfo( type="Video", infoLabels=infoLabels)
            item.setProperty('fanart_image',fanart)
            if int(perpage) < int(total_count):
                total_items = int(perpage)
            else:
                total_items = int(total_count)
            if common.settings['enable_login']=='true' and common.settings['usertoken']:
                cm = []
                cm.append( ('Add to Queue', "XBMC.RunPlugin(%s?mode='addqueue'&url=%s)" % ( sys.argv[0], video_id ) ) )
                if show_id <> '':
                    cm.append( ('Add to Subscriptions', "XBMC.RunPlugin(%s?mode='addsub'&url=%s)" % ( sys.argv[0], show_id ) ) )
                if 'true' == hascaptions:
                    if common.settings['enable_captions'] == 'true':
                        cm.append( ('Play without Subtitles', "XBMC.RunPlugin(%s?mode='NoCaptions_TV_play'&url='%s'&videoid='%s')" % ( sys.argv[0], url, video_id ) ) ) 
                    else:
                        cm.append( ('Play with Subtitles', "XBMC.RunPlugin(%s?mode='Captions_TV_play'&url='%s'&videoid='%s')" % ( sys.argv[0], content_id, video_id ) ) ) 
                    cm.append( ('Assign Subtitles', "XBMC.RunPlugin(%s?mode='SUBTITLE_play'&url='%s'&videoid='%s')" % ( sys.argv[0], content_id, video_id ) ) )
                cm.append( ('Select Quality', "XBMC.RunPlugin(%s?mode='Select_TV_play'&url='%s'&videoid='%s')" % ( sys.argv[0], content_id, video_id ) ) )
                cm.append( ('Vote for Video', "XBMC.RunPlugin(%s?mode='vote'&url=%s)" % ( sys.argv[0], video_id ) ) )
                item.addContextMenuItems( cm ,replaceItems=True) 
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=total_items)


