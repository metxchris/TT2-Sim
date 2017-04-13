This folder hosts the repository's [Wiki](https://metxchris.github.io/TT2-Sim/).

# Todo List
- [x] Sci notation option (you heathens).
- [ ] Finish relic efficiency and add slider plot.
- [ ] Finish adding blue skill-tree skills.
- [ ] Silent March simulations.
- [ ] Include mana calculations (in-progress).
- [ ] Seconds to mins/hrs/days/years function.
- [ ] Improve documentation on formulas used.
- [ ] Overhaul plotting file.

# Update History
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