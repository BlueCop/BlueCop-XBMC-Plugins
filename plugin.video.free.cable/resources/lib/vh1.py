import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import httplib
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common

pluginhandle=int(sys.argv[1])

BASE_URL = 'http://www.vh1.com/video/browse/shows.jhtml'
BASE = 'http://www.vh1.com'

blacklist = [   "14th Annual Critics' Choice Awards (2009)",
                "17th Annual Critics' Choice Movie Awards",
                "40 Winningest Winners of 2011 (Hour 2)",
                '2009 Hip Hop Honors',
                '2010 Hip Hop Honors',
                "America's Most Smartest Model",
                'Behind the Crime Scene: Tupac Shakur',
                'Top 40 Videos of 2009 Hour 2 (20-1)',
                'Top 40 Videos of 2009 Hour 1 (40-21)',
                "Critics' Choice Movie Awards (2010)",
                "Critics' Choice Movie Awards (2011)",
                'DIVAS (2010)',
                'Do Something Awards 2010',
                'Do Something Awards 2011',
                'Front Row',
                'Movies That Rock!',
                'Pop Up Video',
                'Posted',
                'Rock Honors: The Who',
                'Stand Up To Cancer',
                'Top 40 Videos of 2009 Hour 1',
                'Top 40 Videos of 2009 Hour 2',
                'VH1 Big In 2006 Awards',
                'VH1 Divas (2009)',
                'VH1 Divas Celebrates Soul',
                'VH1 Pop Up Video'
                ]

multiseason = [ ['Basketball Wives','Basketball Wives'],
                ['Brandy & Ray J: A Family Business','Brandy & Ray J: A Family Business 2'],
                ['Celebrity Rehab','Celebrity Rehab 5'],
                ['Fantasia For Real','Fantasia For Real 2'],
                ["La La's Full Court Life","La La's Full Court Life"],
                ['Love & Hip Hop','Love & Hip Hop'],
                ['Mob Wives','Mob Wives'],
                ["Rock N' Roll Fantasy Camp","Rock N' Roll Fantasy Camp -  2"],
                ["RuPaul's Drag Race","RuPaul's Drag Race 3"],
                ['Scream Queens','Scream Queens 2'],
                ['Single Ladies','Single Ladies'],
                ['The T.O. Show','The T.O. Show 3'],
                ['Tough Love','Tough Love New Orleans'],
                ['What Chilli Wants','What Chilli Wants 2'],
                ["You're Cut Off!","You're Cut Off!"]
                ]

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    url = 'http://www.vh1.com/shows/all_vh1_shows.jhtml'
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    shows=tree.find('div',attrs={'id':'azshows'}).findAll('a')
    db_shows=[]
    for show in shows:
        name = show.string.replace('Season','').strip()
        url = show['href'].replace('series.jhtml','video.jhtml?sort=descend')
        mode = 'showsubcats'
        if BASE not in url:
            url = BASE + url
        if name in blacklist:
            continue
        elif '/shows/events' in url:
            continue

        docontinue=False
        for series_name,choosen in multiseason:
            if series_name in name:
                if choosen <> name:
                    docontinue=True
                elif choosen == name:
                    name = series_name
                    mode = 'seasons'
        if docontinue:
            continue
        if '(' in name:
            name=name.split('(')[0].strip()
            
        if db:
            db_shows.append((name, 'mtv', mode, url))
        else:
            common.addShow(name,'vh1',mode,url)
    if db:
        return db_shows
    else:
        common.setView('tvshows')
        
def seasons(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    seasonmenu=tree.find('select',attrs={'id':'videolist_id'})
    if seasonmenu:
        seasons = seasonmenu.findAll('option')
        for season in seasons:
            url = BASE + season['value']
            name = season.string
            common.addDirectory(name,'vh1','seasonOptions',url)
        common.setView('seasons')

def seasonOptions(url=common.args.url):
    common.addDirectory('All Videos','vh1','videos',url)
    common.addDirectory('Full Episodes','vh1','videos',url+'fulleps')
    common.addDirectory('Bonus Clips','vh1','videos',url+'bonusclips')
    common.addDirectory('After Shows','vh1','videos',url+'aftershows')
    common.addDirectory('Sneak Peeks','vh1','videos',url+'sneakpeeks')
    common.setView('seasons')

def showsubcats(url=common.args.url):
    #Add season options
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    subs=tree.find(attrs={'class':'group-a'}).findAll('a')
    for sub in subs:
        name = sub.string
        url = sub['href']
        if BASE not in url:
            url = BASE + url
        if name == None:
            name = sub.contents[-1]
        if 'Episodes' in name or 'Clips' in name or 'Peeks' in name or 'Watch' in name or 'Video' in name:
            if 'id=' in url:
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(url)+'"'
                u += '&mode="vh1"'
                u += '&sitemode="playurl"'
                item=xbmcgui.ListItem(name)
                item.setInfo( type="Video", infoLabels={ "Title":name })
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False)
            else:
                common.addDirectory(name,'vh1','videos',url)
    common.setView('seasons')

def videos(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    subs=tree.find(attrs={'class':'group-b'})
    try:
        try:finalsubs = subs.find(attrs={'class':'video-list'}).findAll('tr',attrs={'class':True})
        except:
            try:finalsubs = subs.find(attrs={'id':"vid_mod_1"}).findAll(attrs={'itemscope':True})
            except:finalsubs = tree.find(attrs={'id':"vid_mod_1"}).findAll(attrs={'itemscope':True})
        for sub in finalsubs:
            sub = sub.find('a')
            name = sub.string
            url = sub['href']
            if BASE not in url:
                url = BASE + url
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="vh1"'
            u += '&sitemode="playurl"'
            common.addVideo(u,name,'',infoLabels={ "Title":name })
        common.setView('episodes')
    except:
        print 'No videos'

def playuri(uri = common.args.url,referer='www.vh1.com'):
    mp4_url = "http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639+_pxE=/44620/mtvnorigin"
    mtvn = 'http://media.mtvnservices.com/'+uri 
    swfUrl = common.getRedirect(mtvn)#,referer=referer)
    configurl = urllib.unquote_plus(swfUrl.split('CONFIG_URL=')[1].split('&')[0])
    configxml = common.getURL(configurl)
    tree=BeautifulStoneSoup(configxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    feed = tree.find('player').find('feed')
    try:
        mrssurl = feed.string.replace('{uri}',uri).replace('{ref}','None').replace('&amp;','&').strip()
        mrssxml = common.getURL(mrssurl)
        mrsstree = BeautifulStoneSoup(mrssxml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    except:
        mrsstree = feed
    segmenturls = mrsstree.findAll('media:content')
    stacked_url = 'stack://'
    for segment in segmenturls:
        surl = segment['url']
        videos = common.getURL(surl)
        videos = BeautifulStoneSoup(videos, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('rendition')
        hbitrate = -1
        sbitrate = int(common.settings['quality'])
        for video in videos:
            bitrate = int(video['bitrate'])
            if bitrate > hbitrate and bitrate <= sbitrate:
                hbitrate = bitrate
                rtmpdata = video.find('src').string
                rtmpurl = mp4_url+rtmpdata.split('viacomvh1strm')[2]
                #protocall = rtmpdata.split('://')[0]
                #host = rtmpdata.split('://')[1].split('/')[0]
                #app = rtmpdata.split('://')[1].split('/')[1]
                #playpath = rtmpdata.split(app+'/')[1]
                #if '.mp4' in playpath:
                #    playpath = 'mp4:'+playpath#.replace('.mp4','')
                #else:
                #    playpath = playpath#.replace('.flv','')
                #rtmpurl = 'rtmpe://'+host+':1935/'+app
                #rtmpurl += ' playpath=' + playpath + " swfurl=" + swfUrl.split('?')[0] +" pageUrl=" + referer + " swfvfy=true"
        stacked_url += rtmpurl.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def playurl(url = common.args.url):
    data = common.getURL(url)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    uri = tree.find('link',attrs={'rel':'video_src'})['href'].split('/')[-1]
    playuri(uri,referer=url)
