import os
import xbmc
import xbmcaddon

Addon = xbmcaddon.Addon(id=os.path.basename(os.getcwd()))

class Main:

    def __init__(self):
	#cancel the alarm if it is already running
	xbmc.executebuiltin('CancelAlarm(huluupdatelibrary)')
	
        timer_amounts = {}
        timer_amounts['0'] = '60'
        timer_amounts['1'] = '90'
        timer_amounts['2'] = '120'
        timer_amounts['3'] = '300'
        timer_amounts['4'] = '600'
        
        #only do this if we are not playing anything
        if(xbmc.Player().isPlaying() == False):
            #run the update since we have just started the program
            if(Addon.getSetting('update_video')):
				xbmc.executebuiltin("RunPlugin(plugin://plugin.video.hulu/?mode='QueueLibrary')")
				xbmc.executebuiltin("RunPlugin(plugin://plugin.video.hulu/?mode='SubscriptionsLibrary')")

        
        #reset the timer
        xbmc.executebuiltin('AlarmClock(huluupdatelibrary,XBMC.RunScript(script.hululibraryautoupdate),' +
                            timer_amounts[Addon.getSetting('timer_amount')] +  ',true)')

        xbmc.log('update hulu library add-on complete')
#run the program
run_program = Main()
