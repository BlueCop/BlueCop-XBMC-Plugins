import xbmc
import xbmcplugin

import common
import os
import sys

class Main:
    def __init__( self ):
        if (common.settings["flat_channels"]):
            self.addShowsAsHome()
        else:
            self.addMainHomeItems()

        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )

    
    def addMainHomeItems( self ):
        common.addDirectory("NBC", common.NBC_FULL_URL, "TV_nbc", xbmc.translatePath(os.path.join(common.imagepath,"nbc_posterart.jpg")), xbmc.translatePath(os.path.join(common.imagepath,"nbc_posterart.jpg")), genre = "list", plot = "NBC")
        common.addDirectory("SciFi", common.SCIFI_FULL_URL, "TV_scifi", xbmc.translatePath(os.path.join(common.imagepath,"scifi_posterart.jpg")), xbmc.translatePath(os.path.join(common.imagepath,"scifi_posterart.jpg")), genre = "list", plot = "SciFi")
        common.addDirectory("USA", common.USA_FULL_URL, "TV_usa", xbmc.translatePath(os.path.join(common.imagepath,"usa_posterart.jpg")), xbmc.translatePath(os.path.join(common.imagepath,"usa_posterart.jpg")), genre = "list", plot = "USA")


    def addShowsAsHome( self ):
        import nbc_tv
        common.args.url=common.NBC_FULL_URL
        common.args.mode='TV_nbc'
        nbc_tv.Main()
        
        import scifi_tv
        common.args.url=common.SCIFI_FULL_URL
        common.args.mode='TV_scifi'
        scifi_tv.Main()
        
        import usa_tv
        common.args.url=common.USA_FULL_URL
        common.args.mode='TV_usa'
        usa_tv.Main()
