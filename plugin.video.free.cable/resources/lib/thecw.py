import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import httplib
import sys
import os
import re
import demjson

from BeautifulSoup import BeautifulSoup
import resources.lib._common as common

pluginhandle=int(sys.argv[1])

BASE_URL = 'http://www.cwtv.com/cw-video/'
BASE = 'http://www.cwtv.com'

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    data = common.getURL(BASE_URL)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find('div',attrs={'id':'shows-video'}).findAll('li')
    db_shows = []
    for item in menu:
        url = BASE + item.find('a')['href']
        #thumb = item.find('img')['src']
        showname = item.find('p',attrs={'class':'t'}).string.strip()
        #if showname == 'More Video':
        #    continue
        if db==True:
            db_shows.append((showname,'thecw','show',url))
        else:
            common.addShow(showname, 'thecw', 'show', url)
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')

def show(url=common.args.url):
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find('div',attrs={'id':'videotabs'}).findAll('li')
    for item in menu:
        itemurl = url +'<videotab>'+ item['id'].replace('videotab_','')
        name = item.find('p').string.split('(')[0].title()
        common.addDirectory(name, 'thecw', 'episodes', itemurl)
    common.setView('seasons')

def episodes(url=common.args.url):
    urldata = url.split('<videotab>')
    tabid = int(urldata[1])
    url = urldata[0]
    data = common.getURL(url)
    tree=BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    menu=tree.find(attrs={'id':'cw-content'}).findAll(attrs={'class':'videotabcontents'})
    for item in menu:
        itemid = int(item['id'].replace('videotabcontents_',''))
        if tabid == itemid:
            videos=item.findAll('div',recursive=False)
            for video in videos:
                print video.prettify()
                url = video.find('a')['href'].split('=')[1]
                print url
                thumb = video.find('img')['src']
                name = video.find(attrs={'class':'t1'}).string.title()
                description = video.find(attrs={'class':'d3'}).string
                #try:
                #    description = hoverinfo.contents[2].strip()
                #except:
                #    print 'description failure'
                #    description = ''
                try:
                    airdate = hoverinfo.contents[0].contents[2].replace('Original Air Date: ','')
                except:
                    print 'airdate failure'
                    airdate=''
                try:
                    duration = hoverinfo.contents[0].contents[4].strip()
                except:
                    print 'duration failure'
                    duration = ''
                try:
                    seasonepisode = hoverinfo.contents[0].contents[0].replace('Season ','').split(', EP. ')
                    season = int(seasonepisode[0])
                    episode = int(seasonepisode[1])
                    displayname = '%sx%s - %s' % (str(season),str(episode),name)
                except:
                    displayname = name
                    season = 0
                    episode = 0
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(url)+'"'
                u += '&mode="thecw"'
                u += '&sitemode="play"'
                infoLabels={ "Title":name,
                             "Season":season,
                             "Episode":episode,
                             "Plot":description,
                             "premiered":airdate,
                             "Duration":duration,
                             #"TVShowTitle":common.args.name
                             }
                common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def play(url=common.args.url):
    #rtmpe://wbads.fcod.llnwd.net/a2383/o33/ playpath=mp4:kidswb/channels/video/thundercats_01_exodus_700kbps.mp4
    swfurl = 'http://pdl.warnerbros.com/cwtv/digital-smiths/production_player/vsplayer.swf'
    #swfurl = 'http://media.cwtv.com/cwtv/digital-smiths/production_player/vsplayer.swf'
    url = 'http://metaframe.digitalsmiths.tv/v2/CWtv/assets/%s/partner/132?format=json' % common.args.url
    #jsonurl = 'http://metaframe.digitalsmiths.tv/v2/CWtv/assets/'+url+'/partner/132?format=json'
    data = common.getURL(url)
    print "D",data
    #    data = common.getURL(jsonurl)
    #print demjson.decode(data)['videos']
    #rtmp = demjson.decode(data)['videos']['ds700']['uri']
    #rtmpsplit = rtmp.split('mp4:')
    #74.213.154.10
    #rtmp = rtmpsplit[0]+' playpath=mp4:'+rtmpsplit[1]
    #rtmp = 'rtmpe://74.213.154.10/cwtv/ playpath=mp4:'+rtmpsplit[1]
    #rtmpe://cwtvfs.fplive.net/cwtv/
    items = demjson.decode(data)
    sbitrate = int(common.settings['quality'])
    hbitrate=-1
    lbitrate=-1
    for key in items['videos']:
        item=items['videos'][key]
        print "item",item
        bitrate = int(item['bitrate'])
        #print "BR",bitrate
        print sbitrate,bitrate,hbitrate
        if bitrate < lbitrate or lbitrate==-1:
            lbitrate = bitrate
            #print "BR",bitrate
            lrtmpdata = item['uri'].split('mp4:')
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            print "BR",bitrate
            rtmpdata = item['uri'].split('mp4:')
    if hbitrate==-1:
       dialog = xbmcgui.Dialog()
       line1 = "No video found for maxium bitrate "+common.settings['quality']
       line2 = "Lowest bitrate found is "+str(lbitrate)
       line3 = "Use this bitrate?"
       if dialog.yesno("Free Cable", line1,line2,line3):
          rtmpdata=lrtmpdata
 
 
       #dialog.ok("Free Cable", line1, line2, line3)
      
    #recently there are more than two steams, some of whch have issues need to support all to work around playback
    #if sbitrate > 700:
     #   rtmpdata = items['videos']['ds700']['uri'].split('mp4:')
    #if sbitrate < 700:
    #    rtmpdata = items['videos']['ds500']['uri'].split('mp4:')
    #rtmpdata = items['videos']['ds500']['uri'].split('mp4:')
    rtmp = rtmpdata[0]
    playpath ='mp4:'+rtmpdata[1].replace('Level3','') 
    #'mp4:'+'cwtv/videos/2013/04/24/CW-Arrow-2J7320-HomeInvasion_a68203930_500kbps.mp4'
    #can this be found?
    rtmp = 'rtmpe://wbworldtv.fcod.llnwd.net/a2246/o23/'
    rtmpurl = rtmp+' playpath='+playpath+" swfurl=" + swfurl + " swfvfy=true"
    item = xbmcgui.ListItem(path=rtmpurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)