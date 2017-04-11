# TT2-Sim: A Gameplay Simulator

*Update notes listed [here](https://github.com/metxchris/TT2-Sim/tree/master/docs#update-history).*

TT2-Sim is an analysis focused Tap Titans 2 simulator written in Python.  The design goal of this simulator was to answer several of the many infamous subreddit questions, such as:
- Is it worth buying this thing?
- Can I push to this stage?
- How should I pick my skill-tree?
- How high could I push if there wasn't a stage cap?

From using testing this tool out with others in the subreddit community, we've noticed that the answers to these questions are generally: maybe, yes, it doesn't matter, and the top simulated prediction we've recorded so far is 4895 (calculations above stage 3500 are just an extrapolation of the current model, and will need to be updated when the in-game stage cap is increased).  By entering your current configuration into the PlayerInput.csv file, you can use the simulation to test the impact obtained by changing weapon, pet, and skill-tree configurations yourself.  Moreover, this simulation works well in conjunction with well-known optimizers such as [YATTWO](https://yattwo.me/), as you will now be able to directly observe how your gameplay will change for each suggested optimization.

# Running TT2-Sim
This code was designed to run using Python v3.6+ (see comments in Classes.py for v2.7 compatibility).  In order to use TT2-Sim, you will need to download the repository to a local directory.  The easiest way to set this up with all necessary dependencies is to install the [Anaconda](https://www.continuum.io/downloads) distribution; the installation footprint is quite large compared to what's required to run the sim, but this is the easiest way to get everything working without having to manually install dependencies.  I also recommend running the code through [Sublime Text](https://www.sublimetext.com/); this will allow you to easily run the simulation directly through the text editor (press ctrl+b), instead of having to run everything through the command line.  Initiate the simulation by running the Main.py file.  The Classes.py file is a dependency needed to initialize game data, but can also be run directly to print out a full list of all input variables used in the sim.

# How It Works
The simulation was designed as a a basic version of the TT2 game engine.  While several simplifications are made, the results provide an extremely accurate picture of your game performance in the MS800+ stage range (some of the approximations made may throw off accuracy during the earliest stages, and my ability to test these stages has been limited so far).  The code itself is well-commented, so read through the Main.py file for more details on the processes used.

# Sample Plots and Analysis

<div style="width:1000px;margin-left:150px">
<img src="./images/splash_1000_2710.png" alt="Splash Comparison" width="425" style="float:left; display:inline;"/><img src="./images/dps_tap20.png" alt="Splash Comparison" width="425" style="float:left; display:inline;"/>
</div>

There is great potential for model analysis using TT2-Sim. A full overview of various of results obtained and studies performed using the sim will be posted on the repository's [Wiki](https://metxchris.github.io/TT2-Sim/).

# Sample Text Output

```
    GENERAL RESULTS FOR: MetxChris
    ―――――――――――――――――――――――――――――――――――――――――
    Final Stage: 3875       Boss HP: 367.89cp
    Start Stage: 1100       Damage:  207.14cp
    ――――――――――――――――――――――――――――――――――――――――――――――――――――――
    Hero Levels: [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 4000 3800] 
                 [3460 3040 2540 2540 2540] Total: 141920


    ACTIVE SKILL INFO:
    ―――――――――――――――――――――――――――――――――――――
    Name              Level       Effect 
    ―――――――――――――――――――――――――――――――――――――
    Crit Strike          15        50.00%
    Hand of Midas        15         13.80
    War Cry              15         1.03k
    ―――――――――――――――――――――――――――――――――――――


    DAMAGE RESULTS:
    ―――――――――――――――――――――――――――――――――――――――
    Type            Amount        Bonus    
    ―――――――――――――――――――――――――――――――――――――――
    Total DPS        812.34co      11.40ab%
    Hero DPS         731.75cm       16.00B%
    Melee DPS        731.49cm        1.19B%
    Ranged DPS       167.02cl      202.89k%
    Spell DPS:        90.67cl      110.12k%
    Pet DMG:         609.24co       90.28M%
    Tap DMG:          11.71cm      212.17k%
    Clan DMG:          7.32cn        4.07T%
    ―――――――――――――――――――――――――――――――――――――――
    Crit Chance:                     50.00%
    Crit Max:          196.99
    Crit Min:           29.55
    ―――――――――――――――――――――――――――――――――――――――
    Artifact:                      377.07k%


    GOLD RESULTS:
    ―――――――――――――――――――――――――――――――――――――――
    Type             Amount      Multiplier
    ―――――――――――――――――――――――――――――――――――――――
    Total Earned     550.76cs        10.75k
    Boss Gold        547.07cs        200.80
    Chest Gold         3.54cs         40.70
    Titan Gold       149.82cr         58.13
    TF Chance           1.00%          1.02 †
    10x Chance         22.00%          2.98 ‡
    ―――――――――――――――――――――――――――――――――――――――
    Remaining         23.05cs
    Spent            527.71cs
    ―――――――――――――――――――――――――――――――――――――――
    † Does not multiply with HoM or Bosses.
    ‡ Does not multiply with HoM.


    SPLASH RESULTS BY STAGE (PET ATTACKS):
    ――――――――――――――――――――――――――――――――――――――――――――――――――――
    Splash Amount    Maximum Splash       Minimum Splash
    ――――――――――――――――――――――――――――――――――――――――――――――――――――
              x20              3695                 3553
               x4              3727                 3686
               x3              3729                 3709
               x2              3731                 3711
               x1              3754                 3714
    ――――――――――――――――――――――――――――――――――――――――――――――――――――
    Splash Factor: 0.0636


    HERO EVOLVE STAGES:
    ――――――――――――――――――――――――――――――――――――――――――――――――――――――
    1st Evolve:  [1100 1100 1100 1100 1100 1100 1100 1100] 
                 [1100 1100 1100 1100 1100 1100 1100 1100] 
                 [1100 1100 1100 1100 1100 1100 1100 1100] 
                 [1100 1101 1121 1281 1456 1665 1893 2119] 
                 [2336 2610 2923 2923 2923]
    2nd Evolve:  [1100 1101 1101 1101 1101 1101 1101 1101] 
                 [1110 1126 1139 1156 1176 1204 1215 1236] 
                 [1256 1287 1315 1346 1371 1405 1447 1496] 
                 [1554 1641 1764 1919 2094 2303 2532 2758] 
                 [2973 3247 3562 3562 3562]


    ATTACKS AND TIMES TO REACH STAGE: 3875
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
    Attack Interval    Attacks      Active Time      Wasted Time       Total Time
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
            0.1 sec     46.05k       79.67 mins      144.65 mins      224.32 mins
            0.2 sec     29.21k       94.25 mins      143.05 mins      237.30 mins
            0.3 sec     22.88k      111.67 mins      142.12 mins      253.79 mins
            0.4 sec     19.51k       90.07 mins      141.45 mins      231.52 mins
            0.5 sec     17.45k      120.75 mins      140.92 mins      261.67 mins
            0.6 sec     16.03k      151.08 mins      140.48 mins      291.56 mins
            0.7 sec     15.01k       66.73 mins      140.09 mins      206.82 mins
            0.8 sec     14.26k       81.61 mins      139.82 mins      221.43 mins
            0.9 sec     13.64k       96.19 mins      139.57 mins      235.76 mins
            1.0 sec     13.17k      111.04 mins      139.38 mins      250.42 mins
            1.5 sec     11.70k      184.46 mins      138.34 mins      322.80 mins
            2.0 sec     10.91k      256.02 mins      137.69 mins      393.71 mins
            3.0 sec     10.16k      401.09 mins      136.69 mins      537.78 mins
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
    Tap Attacks          5.99B     4915.52 days        0.13 days     4915.65 days
    Heav. Strikes      461.31k       21.40 days        0.11 days       21.51 days
    Pet Attacks         14.60k       74.01 mins      139.97 mins      213.98 mins
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
    KillAnimationTime + DeviceLag: 0.7 sec
```

# Credit
Special thanks to Marxz13 for collaborating with me on various gameplay aspects, testing for accuracy issues, and being a great community resource.  Also thanks to [Colblitz](https://github.com/colblitz) for helping me find several gameplay formulas I was missing.  Additionally, thanks to Byungshin for helping me nail down a few errors in the gold calculations.