import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import time
import md5
import tempfile
import addoncompat
from BeautifulSoup import BeautifulStoneSoup



try:
    try:
        from pysqlite2 import dbapi2 as sqlite
    except:
        from sqlite3 import dbapi2 as sqlite
    sqliteAvailable = True
except:
    sqliteAvailable = False 

pluginhandle = int (sys.argv[1])
"""
    PARSE ARGV
"""

class _Info:
    def __init__( self, *args, **kwargs ):
        print "common.args"
        print kwargs
        self.__dict__.update( kwargs )

exec "args = _Info(%s)" % (urllib.unquote_plus(sys.argv[2][1:].replace("&", ", ").replace('"','\'')) , )



"""
    DEFINE
"""
site_dict = {'ABC': 'abc',
             'ABC Family':'abcfamily',
             'CBS': 'cbs',
             'NBC': 'nbc',
             'USA': 'usa',
             'SyFy': 'syfy',
             'The CW':'thecw',
             'Spike':'spike',
             'A&E':'aetv',
             'MTV Shows':'mtv',
             'VH1 Shows':'vh1',
             #'TNT': 'tnt',
             #'TBS': 'tbs',
             'History Channel':'history',
             'Lifetime':'lifetime',
             'Bravo':'bravo',
             'Oxygen':'oxygen',
             'Food Network':'food',
             'TV Land':'tvland'
             #'Comedy Central':'comedy',
             #'Adult Swim':'adultswim',
             #'Cartoon Network':'cartoon'
             #'FOX': 'fox',
             #'FX': 'fx',
             #'The Hub':'hub',        
             }

addoncompat.get_revision()
pluginpath = addoncompat.get_path()

db_file = os.path.join(xbmc.translatePath(pluginpath),'resources','shows.db')
cachepath = os.path.join(xbmc.translatePath(pluginpath),'resources','cache')
imagepath = os.path.join(xbmc.translatePath(pluginpath),'resources','images')

"""
    GET SETTINGS
"""

settings={}
#settings general
quality = ['200', '400', '600', '800', '1000', '1200', '1400', '1600', '2000', '2500', '3000', '100000']
selectquality = int(addoncompat.get_setting('quality'))
settings['quality'] = quality[selectquality]
settings['enableproxy'] = addoncompat.get_setting('us_proxy_enable')
settings['enablesubtitles'] = addoncompat.get_setting('enablesubtitles')

def get_series_id(seriesid,seriesname):
    shows = BeautifulStoneSoup(seriesid, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('series')
    names = list(BeautifulStoneSoup(seriesid, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('seriesname'))
    if len(names) > 1:
        select = xbmcgui.Dialog()
        ret = select.select(seriesname, [name.string for name in names])
        if ret <> -1:
            seriesid = shows[ret].find('seriesid').string
    else:
        seriesid = shows[0].find('seriesid').string
    return seriesid

def tv_db_series_lookup(seriesname):
    tv_api_key = '03B8C17597ECBD64'
    mirror = 'http://thetvdb.com'
    banners = 'http://thetvdb.com/banners/'
    series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(seriesname)
    seriesid = getURL(series_lookup)
    try: seriesid = get_series_id(seriesid,seriesname)
    except:
        return False
##        keyb = xbmc.Keyboard(seriesname, 'Manual Search')
##        keyb.doModal()
##        if (keyb.isConfirmed()):
##                series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(keyb.getText())
##                seriesid = getURL(series_lookup)
##                try: seriesid = get_series_id(seriesid,seriesname)
##                except:
##                    print 'manual search failed'
##                    return False
    series_xml = mirror+('/api/%s/series/%s/en.xml' % (tv_api_key, seriesid))
    series_xml = getURL(series_xml)
    tree = BeautifulStoneSoup(series_xml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    try: aired = tree.find('firstaired').string
    except:
        print '%s - Air Date Failed' % seriesname
        aired = ''
    try: genre = tree.find('genre').string
    except:
        print '%s - Genre Failed' % seriesname
        genre = ''
    try: description = tree.find('overview').string
    except:
        print '%s - Description Failed' % seriesname
        description = ''
    try: actors = tree.find('actors').string
    except:
        print '%s - Poster Failed' % seriesname
        actors = ''
    try: rating = float(tree.find('rating').string)
    except:
        print '%s - Rating Failed' % seriesname
        rating = 0.0
    try: banner = banners + tree.find('banner').string
    except:
        print '%s - Banner Failed' % seriesname
        banner = ''
    try: fanart = banners + tree.find('fanart').string
    except:
        print '%s - Fanart Failed' % seriesname
        fanart = ''
    try: poster = banners + tree.find('poster').string
    except:
        print '%s - Poster Failed' % seriesname
        poster = ''
    return [int(seriesid), description, banner, fanart, aired, genre, rating]

def load_db():
    #if os.path.exists(db_file):
    #    os.remove(db_file)
    if not os.path.exists(db_file):
        create_db(db_file)
    conn = sqlite.connect(db_file)
    c = conn.cursor()
    return c.execute('select * from shows order by name')

def update_db(name,mode):
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    showdata = c.execute('select * from shows where name=? and mode=?', (name,mode))
    try:
        tvdb_data = tv_db_series_lookup(showdata[1])
        if tvdb_data is False:
            tvdb_data = [-1,'', '', '', '', '', '']
    except:
        tvdb_data = [-1,'', '', '', '', '', '']
    c.execute('delete from shows where id=?', (showdata[0],))
    showdata[0] = tvdb_data[0]
    for n in range(1,6):
        showdata[n+3] = tvdb_data[1]
    show = tuple(showdata)
    print show
    c.execute('insert into shows values (?,?,?,?,?,?,?,?,?,?,?)', show)
    conn.commit()
    c.close()

def create_db(db_file):
    dialog = xbmcgui.DialogProgress()
    dialog.create('Caching')
    total_stations = len(site_dict)
    current = 0
    increment = 100.0 / total_stations
    conn = sqlite.connect(db_file)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('''create table shows
                (id integer, name text, mode text, sitemode text, url text, description text, poster text, fanart text, aired text, genre text, rating float)''')
    for name , network in site_dict.iteritems():
        percent = int(increment*current)
        exec 'import %s' % network
        exec 'showdata = %s.masterlist()' % network
        for show in showdata:
            dialog.update(percent,'Scanning %s' % name,'Looking up %s' % show[0] )
            try:
                tvdb_data = tv_db_series_lookup(show[0])
                if tvdb_data is False:
                    tvdb_data = [-1,'', '', '', '', '', '']
            except:
                tvdb_data = [-1,'', '', '', '', '', '']
            show = list(show)
            show.insert(0, tvdb_data[0])
            for data in tvdb_data[1:len(tvdb_data)]:
                if data is not None: show.append(data)
                else: show.append('')
            show = tuple(show)
            c.execute('insert into shows values (?,?,?,?,?,?,?,?,?,?,?)', show)
            conn.commit()
            if (dialog.iscanceled()):
                return False
        current += 1
    c.close()

"""
    ADD DIRECTORY
"""

def addDirectory(name, mode='', sitemode='', url='', thumb='', fanart='', description='', aired='', genre='', rating=0.0):
    #if fanart == '':
    #    try:
    #        fanart = args.fanart
    #    except:
    #        pass
    #if thumb == '':
    #    try:
    #        thumb = args.thumb
    #    except:
    #        pass
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    #u += '&thumb="'+urllib.quote_plus(thumb)+'"'
    #u += '&fanart="'+urllib.quote_plus(fanart)+'"'
    u += '&name="'+urllib.quote_plus(name.replace("'",''))+'"'
    item=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
    item.setProperty('fanart_image',fanart)
    item.setInfo( type="Video", infoLabels={ "Title":name,
                                             "Genre":genre,
                                             "premiered":aired,
                                             "Plot":description})
    xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=item,isFolder=True)


def cacheURL( url, values = None, proxy = False, max_age=(30*60),cache_dir=cachepath):
    print 'FREE CABLE --> common :: getHTML :: url = '+url
    if values == None:
        filename = md5.new(url).hexdigest()
    else:
        filename = md5.new(url+str(values)).hexdigest()
    filepath = os.path.join(cache_dir, filename)
    if os.path.exists(filepath):
        if int(time.time()) - os.path.getmtime(filepath) < max_age:
            print int(time.time()) - os.path.getmtime(filepath)
            print max_age
            print 'Returned from Cache'
            return open(filepath).read()
        else:
            os.remove(filepath)

    if proxy == True:
        us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
        print 'Using proxy: ' + us_proxy
        proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)

    if values == None:
        req = urllib2.Request(url)
    else:
        data = urllib.urlencode(values)
        req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    data=response.read()
    response.close()
        
    fd, temppath = tempfile.mkstemp()
    fp = os.fdopen(fd, 'w')
    fp.write(data)
    fp.close()
    os.rename(temppath, filepath)
    print 'Returned from web'
    return data    


def getURL( url , values = None ,proxy = False):
    try:
        if proxy == True:
            us_proxy = 'http://' + addoncompat.get_setting('us_proxy') + ':' + addoncompat.get_setting('us_proxy_port')
            print 'Using proxy: ' + us_proxy
            proxy_handler = urllib2.ProxyHandler({'http':us_proxy})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        print 'FREE CABLE --> common :: getHTML :: url = '+url
        if values == None:
            req = urllib2.Request(url)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        print 'Error reason: ', e
        return False
    else:
        return link
        
    



