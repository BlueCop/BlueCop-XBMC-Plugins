import os
import sys
import xbmc
import xbmcaddon

### get addon info
__addon__       = xbmcaddon.Addon()
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__author__      = __addon__.getAddonInfo('author')
__version__     = __addon__.getAddonInfo('version')
__addonpath__   = __addon__.getAddonInfo('path')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__icon__        = __addon__.getAddonInfo('icon')
__localize__    = __addon__.getLocalizedString

class Main:

    def __init__(self):

        if(len(sys.argv) > 1):
            alarmtype = sys.argv[1]
            logentry = "alarmtype of " + alarmtype
        else:
            startup = "true"
            alarmtype = "none"
            logentry = "no alarmtype (assuming this is the first run)"
            #cancel the startup alarm if it's running
            #this alarm will only get set if you are using the delayed startup to get around the Weather+ conflict
            #it never needs to get reset
            xbmc.executebuiltin('CancelAlarm(huluupdatelibrary)')
                    
        #only do this if we are not playing anything
        if(xbmc.Player().isPlaying() == False):
            #run the update since we have just started the program
            if(__addon__.getSetting('update_queue') == 'true' and (alarmtype == "queue" or startup == "true")):
                #cancel the alarm if it is already running
                xbmc.executebuiltin('CancelAlarm(huluupdatequeue)')
                #run the update
                xbmc.executebuiltin("RunPlugin(plugin://plugin.video.hulu/?mode='QueueLibrary')")
                #reset the timer
                alarmdelay = str((int(__addon__.getSetting('timer_amount_queue'))+1)*60)
                xbmc.executebuiltin('AlarmClock(huluupdatequeue,XBMC.RunScript(script.hululibraryautoupdate,"queue"),'
                                    + alarmdelay +  ',true)')
                #log the results
                xbmc.log('hulu auto update script add-on has requested an update to the library based on the Hulu queue,'
                          + ' next queue udpate in ' + alarmdelay + ' minutes')
            if(__addon__.getSetting('update_subscriptions') == 'true' and (alarmtype == "subscription" or startup == "true")):
                #cancel the alarm if it is already running
                xbmc.executebuiltin('CancelAlarm(huluupdatesubscription)')
                #run the update
                xbmc.executebuiltin("RunPlugin(plugin://plugin.video.hulu/?mode='SubscriptionsLibrary')")
                #reset the timer
                alarmdelay = str((int(__addon__.getSetting('timer_amount_subscriptions'))+1)*60)
                xbmc.executebuiltin('AlarmClock(huluupdatesubscription,XBMC.RunScript(script.hululibraryautoupdate,"subscription"),'
                                    + alarmdelay +  ',true)')
                #log the results
                xbmc.log('hulu auto update script add-on has requested an update to the library based on the Hulu subscriptions,'
                          + ' next subscription udpate in ' + alarmdelay + ' minutes')
        
        xbmc.log('hulu auto update script add-on complete with ' + logentry)
        
#run the program
run_program = Main()
