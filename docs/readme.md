# Update History
###### 2 May 2017
* Rolled back file-structure update after several bug reports.
* Deleted extras folder to keep the presentation simple.
###### 30 April 2017
* ~Updated the file structure for better organization.~
* ~Included extras folder with additional stand-alone codes.~
* Info Docs are now current with TT2 v1.4.
###### 27 April 2017
* Fixed crash with relic efficiency when stage-cap was limited.
* Created AdvancedOptions.CSV with many options to disable engine components (applies to all input profiles).
* Option to specify how many levels to buy per purchase loop (Use LevelsToBuy=1 for brand new accounts).
* Removed some options from player input files (Use AdvancedOptions.CSV now).
* Added seconds to mins/hrs/days/yrs function.
* Fixed some bugs related to missing player input values (e.g., not having pet:evo was ruining pet damage).
* Tap damage plot is updated to work when a tap damage type (from heroes or sword master) is disabled.
###### 22 April 2017
* Added Relic Prestige Efficiency plot.
* Updated most plots to have semi-log axes now; this shows some of the details better.
###### 19 April 2017
* Fixed bug where mana per stage plot crashed if player didn't have mana siphon or manni mana skills.
###### 13 April 2017
* Added scientific notation option.
* Tweaked how time-table handles measurement lag.
###### 11 April 2017
* Added plot for time spent per stage (use the zoom and pan tools).
* Added plot for mana gained per stage (use the zoom and pan tools).
* Splash plot now adjusts domain bounds to only focus on the region where splash changes.
###### 10 April 2017
* Time-table values now average out over a range of measurement lag to reflect imperfect game measurements.
* Player name display in output. 
* Fixed a bug with swapped FS/HOM values (shame on me).
* Clan bonus now works when `ClanLevel` = 0 (thanks marzx13).
###### 9 April 2017
* Enhanced Time-table display.
* Added `DeviceLag` input; this should be calibrated with individual device lag.