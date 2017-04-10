# TT2-Sim: A Gameplay Simulator

*Update notes listed in [docs](https://github.com/metxchris/TT2-Sim/tree/master/docs).*

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
    GENERAL RESULTS:
    ―――――――――――――――――――――――――――――――――――――――――
    Final Stage: 3510       Boss HP:  15.56cj
    Start Stage: 1000       Damage:   11.07cj
    ――――――――――――――――――――――――――――――――――――――――――――――――――――――
    Hero Levels: [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 3850 3490 3140] 
                 [2800 2370 1870 1870 1870] Total: 137260


    DAMAGE RESULTS:
    ―――――――――――――――――――――――――――――――――――――――
    Type            Amount        Bonus    
    ―――――――――――――――――――――――――――――――――――――――
    Total DPS         43.41ci      11.40ab%
    Hero DPS          97.46cg        8.94M%
    Melee DPS         97.43cg        1.19B%
    Ranged DPS        22.31cf      202.89k%
    Spell DPS:        12.08cf      110.12k%
    Pet DMG:          32.56ci       90.28M%
    Tap DMG:           1.56cg      212.17k%
    Clan DMG:        974.61cg        4.07T%
    ―――――――――――――――――――――――――――――――――――――――
    Crit Chance:                     26.00%
    Crit Max:          148.00
    Crit Min:           22.20
    ―――――――――――――――――――――――――――――――――――――――
    Artifact:                      377.07k%


    GOLD RESULTS:
    ―――――――――――――――――――――――――――――――――――――――
    Type             Amount      Multiplier
    ―――――――――――――――――――――――――――――――――――――――
    Total Earned      12.85cl        10.75k
    Boss Gold          9.99cl        200.80
    Chest Gold         1.44cl         40.70
    Titan Gold         1.43cl         58.13
    TF Chance           1.00%          1.02 †
    10x Chance         22.00%          2.98 ‡
    ―――――――――――――――――――――――――――――――――――――――
    Remaining          6.68cl
    Spent              6.17cl
    ―――――――――――――――――――――――――――――――――――――――
    † Does not multiply with HoM or Bosses.
    ‡ Does not multiply with HoM.


    SPLASH RESULTS BY STAGE (PET ATTACKS):
    ――――――――――――――――――――――――――――――――――――――――――――――――――――
    Splash Amount    Maximum Splash       Minimum Splash
    ――――――――――――――――――――――――――――――――――――――――――――――――――――
              x20              3284                 3222
               x4              3334                 3275
               x3              3336                 3277
               x2              3357                 3300
               x1              3360                 3303
    ――――――――――――――――――――――――――――――――――――――――――――――――――――
    Splash Factor: 0.0636


    HERO EVOLVE STAGES:
    ――――――――――――――――――――――――――――――――――――――――――――――――――――――
    1st Evolve:  [1000 1000 1000 1000 1000 1000 1000 1000] 
                 [1000 1000 1000 1000 1000 1000 1000 1000] 
                 [1000 1000 1000 1000 1000 1000 1000 1000] 
                 [1001 1064 1186 1344 1518 1727 1955 2180] 
                 [2398 2670 2984 2984 2984]
    2nd Evolve:  [1041 1056 1066 1080 1097 1116 1135 1150] 
                 [1170 1188 1201 1220 1239 1264 1276 1299] 
                 [1320 1350 1376 1409 1433 1467 1510 1559] 
                 [1616 1704 1826 1981 2156 2365 2594 2819] 
                 [3035 3309    0    0    0]


    ATTACKS AND TIMES TO REACH STAGE: 3510
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
    Attack Interval    Attacks      Active Time      Wasted Time       Total Time
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
            0.1 sec     46.11k       93.51 mins       62.16 mins      155.67 mins
            0.2 sec     26.93k      106.01 mins       61.03 mins      167.04 mins
            0.3 sec     20.40k       88.89 mins       60.37 mins      149.26 mins †
            0.4 sec     17.33k      102.54 mins       59.97 mins      162.51 mins
            0.5 sec     15.34k      114.96 mins       59.65 mins      174.61 mins
            0.6 sec     13.96k      126.83 mins       59.38 mins      186.21 mins
            0.8 sec     12.37k      152.24 mins       58.95 mins      211.19 mins
            1.0 sec     11.41k      177.56 mins       58.63 mins      236.19 mins
            1.5 sec     10.08k      239.50 mins       58.08 mins      297.58 mins
            2.0 sec      9.47k      303.35 mins       57.69 mins      361.04 mins
            3.0 sec      8.75k      425.54 mins       57.09 mins      482.63 mins
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
    Tap Attacks:         6.79B     3928.89 days        0.05 days     3928.94 days ‡
    Heav. Strikes:     370.95k       23.60 days        0.05 days       23.65 days ‡
    Pet Attacks:        12.75k      146.68 mins       59.08 mins      205.76 mins
    ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
    † Monster death animation delay: 0.3 sec
    ‡ Assumes unlimited time for boss fights.
```

# Credit
Special thanks to Marxz13 for collaborating with me on various gameplay aspects, testing for accuracy issues, and being a great community resource.  Also thanks to [Colblitz](https://github.com/colblitz) for helping me find several gameplay formulas I was missing.  Additionally, thanks to Byungshin for helping me nail down a few errors in the gold calculations.