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
import demjson
import resources.lib._common as common

pluginhandle = int (sys.argv[1])

def masterlist():
    showlist=shows(db=True)
    return showlist

def rootlist():
    common.addDirectory('Movies', 'crackle', 'movieGenres', '')
    common.addDirectory('Television', 'crackle', 'showGenres', '')
    common.addDirectory('Originals', 'crackle', 'originals', '')
    #common.addDirectory('Collections', 'crackle', 'collections', '')
    common.setView('seasons')

def build_api_url(list_type,content_type,video_type='all',genres='all',sort='alpha',region='US',format='json',limit=50,ID='',ios=False):
    #LIST TYPES:    browse, popular, recent, details, channel
    #CONTENT TYPES: movies, shows, originals, collections
    #VIDOE TYPES:   all, full, clips, trailers
    #GENRES:        Action_Comedy_Crime_Horror_Sci-Fi_Thriller
    if ios:
        base = 'http://ios-api.crackle.com/Service.svc/'
    else:
        base = 'http://api.crackle.com/Service.svc/'
    if list_type == 'browse':
        api_url = base+list_type+'/'+content_type+'/'+video_type+'/'+genres+'/'+sort+'/'+region+'?format='+format
    elif list_type == 'popular' or list_type == 'recent':
        api_url = base+list_type+'/'+content_type+'/'+video_type+'/'+genres+'/all/'+region+'/'+str(limit)+'?format='+format
    elif list_type == 'channel':
        api_url = base+list_type+'/'+str(ID)+'/folders/'+region+'?format='+format
    elif list_type == 'details':
        #channel or media type
        api_url = base+list_type+'/media/'+str(ID)+'/'+region+'?format='+format
    return api_url

def showGenres(genre=common.args.url):
    #GENRES:        Action_Comedy_Crime_Horror_Sci-Fi_Thriller
    common.addDirectory('All Shows', 'crackle', 'showsByGenre', 'all')
    common.addDirectory('Action', 'crackle', 'showsByGenre', 'Action')
    common.addDirectory('Comedy', 'crackle', 'showsByGenre', 'Comedy')
    common.addDirectory('Crime', 'crackle', 'showsByGenre', 'Crime')
    common.addDirectory('Horror', 'crackle', 'showsByGenre', 'Horror')
    common.addDirectory('Sci-Fi', 'crackle', 'showsByGenre', 'Sci-Fi')
    common.addDirectory('Thriller', 'crackle', 'showsByGenre', 'Thriller')
    common.setView('seasons')

def showsByGenre(genre=common.args.url):
    shows(genre)

def shows(genre,db=False):
    url = build_api_url('browse','shows','all',genre)
    return listCatType(url,db)

def movieGenres(genre=common.args.url):
    #GENRES:        Action_Comedy_Crime_Horror_Sci-Fi_Thriller
    common.addDirectory('All Movies', 'crackle', 'moviesByGenre', 'all')
    common.addDirectory('Action', 'crackle', 'moviesByGenre', 'Action')
    common.addDirectory('Comedy', 'crackle', 'moviesByGenre', 'Comedy')
    common.addDirectory('Crime', 'crackle', 'moviesByGenre', 'Crime')
    common.addDirectory('Horror', 'crackle', 'moviesByGenre', 'Horror')
    common.addDirectory('Sci-Fi', 'crackle', 'moviesByGenre', 'Sci-Fi')
    common.addDirectory('Thriller', 'crackle', 'moviesByGenre', 'Thriller')
    common.setView('seasons')

def showsByGenremoviesByGenre(genre=common.args.url):
    movies(genre)

def movies(genre,db=False):
    url = build_api_url('browse','movies','full',genre)
    return listCatType(url,db,False)

def originals(db=False):
    url = build_api_url('browse','originals')
    return listCatType(url,db)

def collections(db=False):
    url = build_api_url('browse','collections')
    return listCatType(url,db,False)

def listCatType(url,db,showtype=True):
    data = common.getURL(url)
    db_shows=[]
    if data:
        items = demjson.decode(data)['Entries']
        for item in items:
            show_id=str(item['ID'])
            name=item['Name']
            if db==True:
                db_shows.append((name, 'crackle', 'showroot', show_id))
            else:
                if showtype:
                    common.addShow(name, 'crackle', 'showroot', show_id)
                else:
                    plot=item['Description']
                    genre=item['Genre'] 
                    thumb=item['ChannelArtTileLarge'] 
                    fanart=item['ChannelArtLandscape']
                    common.addDirectory(name, 'crackle', 'showroot', show_id, thumb, '', plot, '',genre)
    if db==True:
        return db_shows
    elif showtype:
        common.setView('tvshows')
    else:
        common.setView('seasons')
        
def showroot(id=common.args.url):
    url = build_api_url('channel','',ID=id)
    data = common.getURL(url)
    if data:
        items = demjson.decode(data)['FolderList']
        for item in items:
            if 'Full Episodes'==item['Name'] or 'Television Clips & Trailers'==item['Name'] or 'Minisodes'==item['Name'] or 'Original Series'==item['Name'] or 'Movie'==item['Name'] or 'Movie Clips & Trailers'==item['Name']:
                for season in item['PlaylistList']:
                    for video in season['MediaList']:
                        thumb=video['ThumbnailExternal']
                        ID=str(video['ID'])
                        url = video['DetailsURL']
                        infoLabels={}
                        infoLabels['Title']=video['Title']
                        infoLabels['Duration']=video['Duration']
                        try:infoLabels['Season']=int(video['Season'])
                        except:pass
                        try:infoLabels['Episode']=int(video['Episode'])
                        except:pass
                        infoLabels['MPAA']=video['Rating'] 
                        infoLabels['Genre']=video['Genre'] 
                        infoLabels['TVShowTitle']=video['ParentChannelName'] 
                        infoLabels['Plot']=video['Description']
                        try:infoLabels['AirDate']=common.formatDate(video['ReleaseDate'],'%m/%d/%Y')
                        except: print video['ReleaseDate']
                        displayname=infoLabels['Title']
                        if infoLabels.has_key('Season') or infoLabels.has_key('Episode'):
                            displayname = str(infoLabels['Season'])+'x'+str(infoLabels['Episode'])+' - '+infoLabels['Title']
                        u = sys.argv[0]
                        u += '?url="'+urllib.quote_plus(ID)+'"'
                        u += '&mode="crackle"'
                        u += '&sitemode="play"'
                        common.addVideo(u,displayname,thumb,infoLabels=infoLabels)
    common.setView('episodes')

def make_auth(url):
    hmac_key = 'WEUEVWJPCLTCQQDI'
    sig = hmac.new(hmac_key, url)
    return sig.hexdigest()

def play(url=common.args.url,playrtmp=True):
    # GET DETAILS FROM API
    #url = build_api_url('details','',ID=id,ios=True)
    #data = common.getURL(url)
    #if data:
    #    for mediaUrl in demjson.decode(data)['MediaURLs']:
    #        if mediaUrl['type'] == '480p_1mbps.mp4':
    #            finalurl=mediaUrl['path']

    # GET ID FROM HTTP PAGE
    #data = common.getURL(url)
    #id,paremeters=re.compile("StartPlayer \((.+?), '(.+?)',").findall(data)[0]
    
    #Get file path
    vidwall = 'http://www.crackle.com/app/vidwall.ashx?flags=-1&fm=%s&partner=20' % url
    data = common.getURL(vidwall)
    tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    filepath = tree.find('i')['p']

    if playrtmp:
        # RTMP STREAMING
        rtmpbase = tree.find('channel')['strrtmpcdnurl']
        swfUrl = 'http://www.crackle.com/flash/ReferrerRedirect.ashx'
        finalurl = 'rtmp://'+rtmpbase+'/'+filepath+'480p_1mbps.mp4'+' swfurl='+swfUrl+" swfvfy=true"
    else:
        # HTTP STREAMING
        finalurl = 'http://media-us-am.crackle.com/'+filepath+'480p_1mbps.mp4'

    item = xbmcgui.ListItem(path=finalurl)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    
    
    
    
    