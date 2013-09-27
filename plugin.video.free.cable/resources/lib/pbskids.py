import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import re
import base64

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
#import demjson
import resources.lib._common as common

import coveapi

pluginhandle = int (sys.argv[1])

key='RnJlZUNhYmxlLTgxMzQyMmE5LTg0YWMtNDdjYy1iYzVhLTliMDZhY2NlM2I2YQ=='
secret='MDEyYzcxMDgtNWJiNS00YmFlLWI1MWYtMDRkMTIzNGZjZWRk'

cove = coveapi.connect( base64.b64decode(key), base64.b64decode(secret) )

def masterlist():
    return rootlist(db=True)

def rootlist(db=False):
    start = 0
    count = 200
    db_shows = []
    while start < count:
        data = cove.programs.filter(filter_producer__name='KIDS',order_by='title',limit_start=start)
        results = data['results']
        count = data['count']
        stop = data['stop']
        del data
        for result in results:
            if len(result['nola_root'].strip()) != 0:
                program_id = re.compile( '/cove/v1/programs/(.*?)/' ).findall( result['resource_uri'] )[0]
                name = result['title'].encode('utf-8')
                if db==True:
                    db_shows.append((name, 'pbskids', 'show', program_id))
                else:
                    common.addShow(name, 'pbskids', 'show', program_id)
        start = stop
    if db==True:
        return db_shows
    else:
        common.setView('tvshows')
        
        
def show(program_id=common.args.url):
    start = 0
    count = 200
    clips = False
    data = cove.videos.filter(fields='associated_images,mediafiles',filter_program=program_id,order_by='-airdate',filter_availability_status='Available',limit_start=start,filter_type='Episode',filter_mediafile_set__video_encoding__mime_type='video/mp4')
    if data['count'] == 0:
        clips = True
        data = cove.videos.filter(fields='associated_images,mediafiles',filter_program=program_id,order_by='-airdate',filter_availability_status='Available',limit_start=start,filter_mediafile_set__video_encoding__mime_type='video/mp4')
    videos = data['results']
    total = data['count']
    stop = data['stop']
    for video in videos:
        infoLabels={}
        try:thumb=video['associated_images'][0]['url']
        except:thumb=video['associated_images'][0]['url']
        url=video['mediafiles'][0]['video_data_url']
        infoLabels['Title']=video['title']
        infoLabels['Plot']=video['long_description']
        infoLabels['Premiered']=video['airdate'].split(' ')[0]
        infoLabels['TVShowTitle']=common.args.name
        infoLabels['Duration']=str(int(video['mediafiles'][0]['length_mseconds'])/1000)
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="pbskids"'
        u += '&sitemode="play"'
        print "U1U",u
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
            u += '&mode="pbskids"'
            u += '&sitemode="play"'
            print "U*U",u
            common.addVideo(u,infoLabels['Title'],thumb,infoLabels=infoLabels)
        start = stop
    common.setView('episodes')

def play():
    print "IN KIDS"
    #smilurl=common.args.url+'&format=SMIL'
    redirecturl=common.args.url
    finalurl=common.getRedirect(redirecturl)
    print "resolved url",finalurl
    #data = common.getURL(smilurl)
    #print "data",data
    #tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    #print "tree",tree.prettify()
    #base = tree.find('meta')
    #print "base",base
    #base='rtmp://s3h56pp78s3goi.cloudfront.net/cfx/st/mp4:cove2.0/wordgirl/634cc2f8-e5bc-4c20-bf85-9cc78ddaf48c/hd-mezzanine-16x9/WORG309_EpisodeA_M1080-16x9-mp4-1200k.mp4
    #base='rtmp://s3h56pp78s3goi.cloudfront.net/cfx/st/'
    #playpath='mp4:cove2.0/wordgirl/634cc2f8-e5bc-4c20-bf85-9cc78ddaf48c/hd-mezzanine-16x9/WORG309_EpisodeA_M1080-16x9-mp4-1200k.mp4'
    #finalurl = base+' playpath='+playpath  
   #playpath=tree.find('ref')['src']
   # if '.mp4' in playpath:
         #playpath = 'mp4:'+playpath
          #  else:
           #     playpath = playpath.replace('.flv','')
           # finalurl = base+' playpath='+playpath   
   #if base:
     #   base = base['base']
      #  if 'rtmp://' in base:
       #     playpath=tree.find('ref')['src']
        #    if '.mp4' in playpath:
         #       playpath = 'mp4:'+playpath
          #  else:
           #     playpath = playpath.replace('.flv','')
           # finalurl = base+' playpath='+playpath
       # elif 'http://' in base:
        #    playpath=tree.find('ref')['src']
     #       finalurl = base+playpath
   # else:
    #    finalurl=tree.find('ref')['src']
   # finalurl=smilurl
   # print "URL",finalurl
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)