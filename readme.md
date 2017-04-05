# TT2-Sim: A Gameplay Simulator

TT2-Sim is a analysis focused Tap Titans 2 simulator written in Python.  The design goal of this simulator was to answer several of the many infamous subreddit questions, such as:
- Is it worth buying this thing?
- Can I push to this stage?
- How should I pick my skill-tree?
- How high could I push if there wasn't a stage cap?

From using testing this tool out with others in the subreddit community, we've noticed that the answers to these questions are generally: maybe, yes, it doesn't matter, and the top simulated prediction we've recorded so far is 4895.  By entering your current configuration into the PlayerInput.csv file, you can use the simulation to test the impact obtained by changing weapon, pet, and skill-tree configurations yourself.  Moreover, this simulation works well in conjunction with well-known optimizers such as [YATTWO](https://yattwo.me/), as you will now be able to directly observe how your gameplay will change for each suggested optimization.

# Running TT2-Sim
This code was designed to run using Python v3.6+ (It might still work in v2.7 if you replace all instances of dtype=str with dtype=np.string_ in Classes.py).  In order to use TT2-Sim, you will need to download the repository to a local directory.  The easiest way to set this up with all necessary dependencies is to install the [Anaconda](https://www.continuum.io/downloads) distribution; the installation footprint is quite large compared to what's required to run the sim, but this is the easiest way to get everything working without having to manually install dependencies.  I also recommend running the code through [Sublime Text](https://www.sublimetext.com/); this will allow you to easily run the simulation directly through the text editor (press ctrl+b), instead of having to run everything through the command line.  Initiate the simulation by running the Main.py file.  The Classes.py file is a dependency needed to initialize game data, but can also be run directly to print out a full list of all input variables used in the sim.

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
        Final Stage: 3570, Boss HP: 23.81ck, Damage: 17.54ck
        Hero Levels: [4000 4000 4000 4000 4000 4000 4000 4000] 
                     [4000 4000 4000 4000 4000 4000 4000 4000] 
                     [4000 4000 4000 4000 4000 4000 4000 4000] 
                     [4000 4000 4000 4000 4000 4000 3650 3300] 
                     [2960 2540 1999 1999 1999] Total: 138447

    DAMAGE RESULTS:
        Total DPS:   53.15cj        All Bonus:    535.90aa%
        Hero DPS:   164.08ch        Hero Bonus:    482.31M%
        Melee DPS:  164.05ch        Melee Bonus:   908.63M%
        Ranged DPS:  20.92cg        Ranged Bonus:   86.50k%
        Spell DPS:   10.89cg        Spell Bonus:    60.22k%
        Pet DMG:     53.15cj        Pet Bonus:      63.99M%
        Tap DMG:      2.63ch        Tap Bonus:      45.60k%
        Ship DMG:     1.64ci        Clan Bonus:      2.50T%
        Crit Max:     148.00        Artifact:      348.61k%
        Crit Min:      22.20        Crit Chance:     36.00%

    GOLD RESULTS:
        Total Earned:    2.44cn     Multiplier:    8.81k
        Boss Gold:       2.43cn     Multiplier:   200.80
        Chest Gold:     10.37cm     Multiplier:    24.42
        Titan Gold:      1.84cm     Multiplier:    46.50
        10x Chance:      22.00%     Multiplier:     2.98  *
        TF Chance:        1.00%     Multiplier:     1.02  **
        Remaining:       2.28cn     Spent:      160.49cm

        *  No bonus with HoM.
        ** No bonus with HoM or Bosses.

    STAGE COMPLETION TIMES (TITANS ONLY):
         1 Second  Per Stage: Stage = 3469
         5 Seconds Per Stage: Stage = 3520
        15 Seconds Per Stage: Stage = 3547
        75 Seconds Per Stage: Stage = 3560

    SPLASH RESULTS (PET ATTACKS):
        Maximum Splash Stage:       x20: 3421   x4: 3473 
                                    x3:  3476   x2: 3501
        Continuous Splash Stage:    x20: 3364   x4: 3418 
                                    x3:  3439   x2: 3464
        Splash Factor: 0.0504

    HERO EVOLVE STAGES:
        1st Evolve:  [ 366  384  391  404  421  436  459  471] 
                     [ 494  512  525  542  561  586  601  620] 
                     [ 641  673  698  730  751  787  833  879] 
                     [ 936 1023 1146 1304 1478 1686 1915 2140] 
                     [2358 2631 2945 2945 2945]
        2nd Evolve:  [1001 1015 1026 1043 1056 1071 1095 1110] 
                     [1129 1147 1160 1179 1198 1225 1236 1258] 
                     [1279 1310 1336 1369 1392 1426 1470 1519] 
                     [1575 1663 1786 1941 2116 2325 2554 2780] 
                     [2995 3269    0    0    0]

    ATTACKS AND TIMES TO REACH STAGE: 3570
        Heavenly Strikes:    77.76k         Time Required:   4.50 days
        Pet Attacks:          9.94k         Time Required: 165.70 mins
        Minimum Possible:     2.36k         Time Required:  39.26 mins
        Transition Screens:   2.36k         Time Wasted:    23.80 mins
```

# Credit
Special thanks to Marxz13 for collaborating with me on various gameplay aspects, testing for accuracy issues, and being a great community resource.  Also thanks to [Colblitz](https://github.com/colblitz) for helping me find several gameplay formulas I was missing.  Additionally, thanks to Byungshin for helping me nail down a few errors in the gold calculations.