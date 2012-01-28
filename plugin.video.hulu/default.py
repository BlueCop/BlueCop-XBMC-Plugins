"""
        Plugin for streaming media from Hulu.com
"""
#main imports
import sys
import os
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

import resources.lib.common as common


print sys.argv
#plugin constants
__plugin__ = "Hulu"
__authors__ = "BlueCop, hyc, rwparris2, retalogic"
__credits__ = "zoltar12 for the original hulu plugin, BlueCop for h264 & flv url changes"


#temp#
print "\n\n\n\n\n\n\nstart of HULU plugin\n\n\n\n\n\n"
try:print "HULU--> common.args.mode -- > " + common.args.mode
except: print "HULU--> no mode has been defined"
#end temp#


def modes( ):
        if sys.argv[2]=='':
            import resources.lib._home as home
            home.Main()
        elif common.args.mode.endswith('Library'):
            import resources.lib.xbmclibrary as xbmclibrary
            xbmclibrary.Main()
        elif common.args.mode.endswith('_play'):
            import resources.lib.stream_hulu as stream_media
            stream_media.Main()
        elif common.args.mode.endswith('Menu') or common.args.mode.endswith('Page'):
            import resources.lib._menu as menu
            menu.Main()
        elif common.args.mode.endswith('Search'):
            import resources.lib._search as search
            search.Main()
        elif common.args.mode.endswith('Queue') or common.args.mode.endswith('Subscriptions') or common.args.mode.endswith('History'):
            import resources.lib._menu as queue
            queue.Main()
        elif common.args.mode.endswith('viewcomplete'):
            common.viewcomplete()    
        elif common.args.mode.endswith('queue') or common.args.mode.endswith('sub') or common.args.mode.endswith('history') or common.args.mode.endswith('vote'):
            common.queueEdit()
        else:
            xbmcgui.Dialog().ok('common.args.mode',common.args.mode)
            print "unknown mode--> "+common.args.mode

if ( __name__ == "__main__" ):
        modes ( )

sys.modules.clear()
