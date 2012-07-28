import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
#import demjson
import resources.lib._common as common

import coveapi

pluginhandle = int (sys.argv[1])

key='FreeCable-813422a9-84ac-47cc-bc5a-9b06acce3b6a'
secret='012c7108-5bb5-4bae-b51f-04d1234fcedd'

cove = coveapi.connect(key, secret)

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    start = 0
    count = 200
    db_shows = []
    while start < count:
        data = cove.programs.filter(filter_producer__name='PBS',order_by='title',limit_start=start)
        results = data['results']
        count = data['count']
        stop = data['stop']
        del data
        for result in results:
            if len(result['nola_root'].strip()) != 0:
                program_id = re.compile( '/cove/v1/programs/(.*?)/' ).findall( result['resource_uri'] )[0]
                name = result['title'].encode('utf-8')
                if db==True:
                    db_shows.append((name, 'pbs', 'show', program_id))
                else:
                    common.addShow(name, 'pbs', 'show', program_id)
        start = stop
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
        
        
def show(program_id=common.args.url):
    start = 0
    count = 200
    clips = False
    data = cove.videos.filter(fields='associated_images,mediafiles',filter_program=program_id,order_by='-airdate',filter_availability_status='Available',limit_start=start,filter_type='Episode')
    if data['count'] == 0:
        clips = True
        data = cove.videos.filter(fields='associated_images,mediafiles',filter_program=program_id,order_by='-airdate',filter_availability_status='Available',limit_start=start)
    videos = data['results']
    total = data['count']
    stop = data['stop']
    for video in videos:
        infoLabels={}
        try:thumb=video['associated_images'][2]['url']
        except:thumb=video['associated_images'][0]['url']
        url=video['mediafiles'][0]['video_data_url']
        infoLabels['Title']=video['title']
        infoLabels['Plot']=video['long_description']
        infoLabels['Premiered']=video['airdate'].split(' ')[0]
        infoLabels['TVShowTitle']=common.args.name
        infoLabels['Duration']=str(int(video['mediafiles'][0]['length_mseconds'])/1000)
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="pbs"'
        u += '&sitemode="play"'
        common.addVideo(u,infoLabels['Title'],thumb,infoLabels=infoLabels)
    start = stop
    while start < count:
        if clips:
            data = cove.videos.filter(fields='associated_images,mediafiles',filter_program=program_id,order_by='-airdate',filter_availability_status='Available',limit_start=start)
        else:
            data = cove.videos.filter(fields='associated_images,mediafiles',filter_program=program_id,order_by='-airdate',filter_availability_status='Available',limit_start=start,filter_type='Episode')
        videos = data['results']
        total = data['count']
        stop = data['stop']
        del data
        for video in videos:
            infoLabels={}
            try:thumb=video['associated_images'][2]['url']
            except:thumb=video['associated_images'][0]['url']
            url=video['mediafiles'][0]['video_data_url']
            infoLabels['Title']=video['title']
            infoLabels['Plot']=video['long_description']
            infoLabels['Premiered']=video['airdate'].split(' ')[0]
            infoLabels['TVShowTitle']=common.args.name
            infoLabels['Duration']=str(int(video['mediafiles'][0]['length_mseconds'])/1000)
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="pbs"'
            u += '&sitemode="play"'
            common.addVideo(u,infoLabels['Title'],thumb,infoLabels=infoLabels)
        start = stop
    common.setView('episodes')

def play():
    smilurl=common.args.url+'&format=SMIL'
    data = common.getURL(smilurl)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    base = tree.find('meta')
    if base:
        base = base['base']
        if 'rtmp://' in base:
            playpath=tree.find('ref')['src']
            if '.mp4' in playpath:
                playpath = 'mp4:'+playpath
            else:
                playpath = playpath.replace('.flv','')
            finalurl = base+' playpath='+playpath
        elif 'http://' in base:
            playpath=tree.find('ref')['src']
            finalurl = base+playpath
    else:
        finalurl=tree.find('ref')['src']
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)




        
        
        
        