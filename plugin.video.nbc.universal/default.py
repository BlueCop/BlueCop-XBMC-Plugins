"""
        Plugin for streaming media from nbc.com, scifi.com and usa.com
"""
#main imports
import sys
import os
import urllib
import xbmc
import xbmcgui
import xbmcplugin

import resources.lib.common as common
import pyamf

#plugin constants
__plugin__ = "NBC Universal"
__authors__ = "bluecop, jonm42, rwparris2"
__credits__ = "BlueCop for initial revision, jonm42 for new scrapers and control structure, rwparris2 for Hulu base code"
__version__ = "1.2"


print "\n\n\n\n\n\n\nstart of NBC Unversal plugin\n\n\n\n\n\n"
try:
    print "NBC --> common.args.mode -- > " + common.args.mode
    network=common.args.mode.split('_')[-1]
except:
    print "NBC --> no mode has been defined"


def modes( ):

    if sys.argv[2]=='':
        import resources.lib._home as home
        home.Main()
    elif common.args.mode.count('_play_'):
        exec "from resources.lib.%s_tv import playRTMP" % (network)
        playRTMP()
    elif common.args.mode.startswith('TV'):
        exec "import resources.lib.%s_tv as tv" % (network)
        tv.Main()
    elif common.args.mode.startswith('Movie'):
        import resources.lib._movie as movie
        movie.Main()
    elif common.args.mode.startswith('RSS'):
        import resources.lib._rss as rss
        rss.Main()
    elif common.args.mode.startswith('HD'):
        import resources.lib._hd as hd
        hd.Main()
    elif common.args.mode.startswith('SUBSCRIPTIONS'):
        import resources.lib._subscriptions as subscriptions
        subscriptions.Main()
    else:
        import xbmcgui
        xbmcgui.Dialog().ok('common.args.mode',common.args.mode)
        print "unknown mode--> "+common.args.mode


if ( __name__ == "__main__" ):
    modes ( )
             
sys.modules.clear()
