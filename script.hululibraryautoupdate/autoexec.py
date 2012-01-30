import xbmc

#use this if you are running Weather+ to avoid a startup conflict
#xbmc.executebuiltin('AlarmClock(huluupdatelibrary,XBMC.RunScript(script.hululibraryautoupdate),1,true)')

#otherwise this one should be fine
xbmc.executebuiltin('RunScript(script.hululibraryautoupdate)')
