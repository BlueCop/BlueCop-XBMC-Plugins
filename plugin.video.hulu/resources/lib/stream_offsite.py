import xbmc
import xbmcgui
import xbmcplugin
import common
import sys

pluginhandle = int(sys.argv[1])

class Main:

    def __init__( self ):
        self.play()

    def play( self ):
        source_site = common.args.sourcesite

        cn_sites = ('Adult Swim','Cartoon Network')

        tnt_tbs_sites = ('TNT','TBS')
        
        viacom_sites = ('MTV','VH1','Comedy Central','The Daily Show','South Park Digital Studios','Spike','TV Land','CMT','Atom','Logo','Nickelodeon','NickJr','Game Trailers')
        
        if source_site in 'CBS':
            import cbs
            url = cbs.GETVIDEO(common.args.url)
        elif source_site in viacom_sites:
            import viacom
            url = viacom.GETVIDEO(common.args.url)
        elif source_site in tnt_tbs_sites:
            import tnt_tbs
            url = tnt_tbs.GETVIDEO(common.args.url)
        elif source_site in 'Revision3':
            import revision3
            url = revision3.GETVIDEO(common.args.url)
        elif source_site in 'Funny or die':
            import funny_or_die
            url = funny_or_die.GETVIDEO(common.args.url)
        elif source_site in cn_sites:
            import cartoon_network
            url = cartoon_network.GETVIDEO(common.args.url)
        elif source_site in 'HBO':
            import hbo
            url = hbo.GETVIDEO(common.args.url)
        else:
            xbmcgui.Dialog().ok('Unsupported External Link',source_site+' is not supported for playback.\nPlease post a request for support.')
            item = xbmcgui.ListItem()
            return xbmcplugin.setResolvedUrl(pluginhandle, False,item)

        
        if url == False:
            item = xbmcgui.ListItem()
            xbmcplugin.setResolvedUrl(pluginhandle, False, item)
        else:
            print url
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)

