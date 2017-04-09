# TT2-Sim: A Gameplay Simulator

TT2-Sim is a analysis focused Tap Titans 2 simulator written in Python.  The design goal of this simulator was to answer several of the many infamous subreddit questions, such as:
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
    -----------------------------------------
    Final Stage: 3770       Boss HP: 982.84cn
    Start Stage: 1550       Damage:  637.18cn
    ------------------------------------------------------
    Hero Levels: [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 4000 4000] 
                 [4000 4000 4000 4000 4000 4000 3960 3600] 
                 [3260 2840 2340 2340 2340] Total: 140680


    DAMAGE RESULTS:
    ---------------------------------------
    Type            Amount        Bonus    
    ---------------------------------------
    Total DPS          2.50cn       8.51ab%
    Hero DPS           2.71cl        1.78B%
    Melee DPS          2.71cl        1.19B%
    Ranged DPS       619.29cj      202.89k%
    Spell DPS:       336.26cj      110.12k%
    Pet DMG:           1.87cn       90.28M%
    Tap DMG:          43.42ck      212.17k%
    Clan DMG:         27.14cl        3.04T%
    ---------------------------------------
    Crit Chance:                     50.00%
    Crit Max:          162.81
    Crit Min:           24.42
    ---------------------------------------
    Artifact:                      377.07k%


    GOLD RESULTS:
    ---------------------------------------
    Type             Amount      Multiplier
    ---------------------------------------
    Total Earned     123.36cq        10.75k
    Boss Gold        122.37cq        200.80
    Chest Gold       871.31cp         40.70
    Titan Gold       115.88cp         58.13
    TF Chance           1.00%          1.02 †
    10x Chance         22.00%          2.98 ‡
    ---------------------------------------
    Remaining         48.03cq
    Spent             75.33cq
    ---------------------------------------
    † Does not multiply with HoM or Bosses.
    ‡ Does not multiply with HoM.


    SPLASH RESULTS BY STAGE (PET ATTACKS):
    ----------------------------------------------------
    Splash Amount    Maximum Splash    Continuous Splash
    ----------------------------------------------------
              x20              3613                 3515
               x4              3645                 3545
               x3              3646                 3546
               x2              3649                 3549
               x1              3652                 3552
    ----------------------------------------------------
    Splash Factor: 0.0636


    HERO EVOLVE STAGES:
    ------------------------------------------------------
    1st Evolve:  [1550 1550 1550 1550 1550 1550 1550 1550] 
                 [1550 1550 1550 1550 1550 1550 1550 1550] 
                 [1550 1550 1550 1550 1550 1550 1550 1550] 
                 [1550 1550 1550 1550 1551 1685 1913 2139] 
                 [2356 2630 2943 2943 2943]
    2nd Evolve:  [1550 1550 1550 1550 1550 1550 1550 1550] 
                 [1550 1550 1550 1550 1550 1550 1550 1550] 
                 [1550 1550 1550 1550 1550 1550 1551 1551] 
                 [1574 1661 1785 1940 2114 2324 2552 2778] 
                 [2994 3267 3583 3583 3583]


    ATTACKS AND TIMES TO REACH STAGE: 3770
    -------------------------------------------
    Attack Interval    Attacks    Time Required
    -------------------------------------------
            0.1 sec     42.71k      115.47 mins
            0.2 sec     25.16k      127.45 mins
            0.3 sec     19.24k      111.00 mins †
            0.4 sec     16.32k      123.61 mins
            0.5 sec     14.57k      136.22 mins
            0.6 sec     13.35k      148.29 mins
            0.8 sec     11.90k      173.51 mins
            1.0 sec     11.02k      198.48 mins
            1.5 sec      9.79k      259.65 mins
            2.0 sec      9.22k      322.07 mins
            3.0 sec      8.60k      444.60 mins
    -------------------------------------------
    Heav. Strikes:     345.78k       22.02 days
    Pet Attacks:        12.21k      167.40 mins
    Transitions:           444       14.80 mins
    -------------------------------------------
    † Monster Death Animation Delay: 0.3 sec
```

# Credit
Special thanks to Marxz13 for collaborating with me on various gameplay aspects, testing for accuracy issues, and being a great community resource.  Also thanks to [Colblitz](https://github.com/colblitz) for helping me find several gameplay formulas I was missing.  Additionally, thanks to Byungshin for helping me nail down a few errors in the gold calculations.