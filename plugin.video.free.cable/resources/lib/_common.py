import xbmcplugin
import xbmc
import xbmcgui
import urllib
import urllib2
import sys
import os
import addoncompat

try:
    from pysqlite2 import dbapi2 as sqlite
except:
    from sqlite3 import dbapi2 as sqlite

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
             'FOX': 'fox',
             'The CW':'thecw',
             'FX': 'fx',
             'TNT': 'tnt',
             'TBS': 'tbs',
             'Spike':'spike',
             'TV Land':'tvland'
             }


"""
    GET SETTINGS
"""

settings={}
#settings general
quality = ['200', '400', '600', '800', '1000', '1200', '1400', '1600', '2000', '2500', '3000', '100000']
selectquality = int(addoncompat.get_setting('quality'))
settings['quality'] = quality[selectquality]
settings['enableproxy'] = addoncompat.get_setting('us_proxy_enable')


def load_db():
    db_file = os.path.join(os.getcwd().replace(';', ''),'resources','shows.db')
    #if os.path.exists(db_file):
    #    os.remove(db_file)
    if not os.path.exists(db_file):
        create_db(db_file)
    conn = sqlite.connect(db_file)
    c = conn.cursor()
    return c.execute('select * from shows order by name')

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
                (name text, mode text, sitemode text, url text, description text, poster text, fanart text)''')
    for name , network in site_dict.iteritems():
        percent = increment*current
        dialog.update(percent,'Caching shows...','Scanning %s' % name)
        exec 'import %s' % network
        exec 'showdata = %s.masterlist()' % network
        for show in showdata:
            c.execute('insert into shows values (?,?,?,?,?,?,?)', show)
        current += 1
    conn.commit()
    c.close()

"""
    ADD DIRECTORY
"""

def addDirectory(name, mode='', sitemode='', url='', thumb=''):
    ok=True
    u  = sys.argv[0]
    u += '?url="'+urllib.quote_plus(url)+'"'
    u += '&mode="'+mode+'"'
    u += '&sitemode="'+sitemode+'"'
    u += '&name="'+urllib.quote_plus(name.replace("'",''))+'"'
    liz=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
    liz.setInfo( type="Video", infoLabels={ "Title":name })
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    return ok


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
        print 'Error reason: ', e.reason
        return False
    else:
        return link
        
    



