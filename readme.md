# TT2-Sim: A Gameplay Simulator

TT2-Sim is a analysis focused Tap Titans 2 simulator written in Python.  The design goal of this simulator was to answer several of the many infamous subreddit questions, such as:
- Is it worth buying this thing?
- Can I push to this stage?
- How should I pick my skill-tree?
- How high could I push if there wasn't a stage cap?

From using testing this tool out with others in the subreddit community, we've noticed that the answers to these questions are generally: no, yes, it doesn't matter, and the top simulated prediction we've recorded so far is 4895.  By entering your current configuration into the PlayerInput.csv file, you can use the simulation to test the impact obtained by changing weapon, pet, and skill-tree configurations yourself.  Moreover, this simulation works well in conjunction with well-known optimizers such as [YATTWO](https://yattwo.me/), as you will now be able to directly observe how your gameplay will change for each suggested optimization.

# Running TT2-Sim
In order to use TT2-Sim, you will need to download the repository to a local directory, where a local installation of Python v2/v3 is required to run the code (I haven't tested this in Python v3 yet but it should be compatible).  The easiest way to set this up with all necessary dependencies is to install the [Anaconda](https://www.continuum.io/downloads) distribution, although the installation footprint is fairly large compared to what's required to run the sim.  I also recommend running the code through [Sublime Text](https://www.sublimetext.com/); this will allow you to easily run the simulation directly through the text editor (press ctrl+b), instead of having to run everything through the command line.  Initiate the simulation by running the Main.py file.  The Classes.py file is a dependency needed to initialize game data, but can also be run directly to print out a full list of all input variables used in the sim.

# How It Works
The simulation was designed as a a basic version of the TT2 game engine.  While several simplifications are made, the results provide an extremely accurate picture of your game performance in the MS800+ stage range (some of the approximations made may throw off accuracy during the earliest stages, and my ability to test these stages has been limited so far).  The code itself is well-commented, so read through the Main.py file for more details on the processes used.

# Sample Plots and Analysis

<div style="width:1000px;margin-left:150px">
<img src="./images/splash_1000_2710.png" alt="Splash Comparison" width="425" style="float:left; display:inline;"/><img src="./images/dps_tap20.png" alt="Splash Comparison" width="425" style="float:left; display:inline;"/>
</div>

There is great potential for model analysis using TT2-Sim. A full overview of various of results obtained and studies performed using the sim will be posted on the repository's [Wiki](https://metxchris.github.io/TT2-Sim/).

# Sample Text Output

```Markdown
    GENERAL RESULTS:
        Final Stage: 3350, Boss HP: 50.07cg, Damage: 48.23cg
        Hero Levels: [4000 4000 4000 4000 4000 4000 4000 4000] 
                     [4000 4000 4000 4000 4000 4000 4000 4000] 
                     [4000 4000 4000 4000 4000 4000 4000 4000] 
                     [4000 4000 4000 4000 3920 3590 3240 2890] 
                     [2540 2120 1620 1620 1620] Total: 135160

    DAMAGE RESULTS:
        Total DPS:  146.20cf        All Bonus:    313.33aa%
        Hero DPS:   617.20cd        Hero Bonus:      4.16M%
        Melee DPS:  617.02cd        Melee Bonus:   908.63M%
        Ranged DPS: 118.34cc        Ranged Bonus:   86.50k%
        Spell DPS:   61.44cc        Spell Bonus:    60.22k%
        Pet DMG:    146.14cf        Pet Bonus:      63.99M%
        Tap DMG:      9.88cd        Tap Bonus:      43.80k%
        Ship DMG:     6.17ce        Clan Bonus:      1.46T%
        Crit Max:     148.00        Artifact:      348.61k%
        Crit Min:      22.20        Crit Chance:     26.00%

    GOLD RESULTS:
        Total Earned:   30.20ci     Multiplier:   8.81k
        Boss Gold:      26.32ci     Multiplier:  200.80
        Chest Gold:      1.65ci     Multiplier:   24.42
        Titan Gold:      2.24ci     Multiplier:   46.50
        Remaining:      13.09ci
        Spent:          17.11ci

    STAGE COMPLETION TIMES (TITANS ONLY):
         5 Seconds Per Stage: Stage = 3199
        15 Seconds Per Stage: Stage = 3228
        75 Seconds Per Stage: Stage = 3303

    SPLASH RESULTS (PET ATTACKS):
        Maximum Splash Stage:       x20: 3054   x4: 3130 
                                    x3:  3154   x2: 3180
        Continuous Splash Stage:    x20: 2947   x4: 2963 
                                    x3:  2966   x2: 2972
        Splash Factor: 0.0504

    HERO EVOLVE STAGES:
        1st Evolve:  [ 409  426  435  451  465  483  501  514] 
                     [ 536  555  567  585  605  626  648  661] 
                     [ 685  716  741  773  794  831  876  921] 
                     [ 979 1061 1189 1346 1520 1730 1957 2183] 
                     [2400 2673 2986 2986 2986]
        2nd Evolve:  [1043 1058 1071 1081 1100 1118 1137 1152] 
                     [1171 1190 1203 1221 1241 1266 1279 1301] 
                     [1321 1351 1379 1411 1431 1470 1511 1561] 
                     [1618 1710 1825 1984 2158 2367 2596 2821] 
                     [3036 3311    0    0    0]
```

# Credit
Special thanks to Marxz13 for collaborating with me on various gameplay aspects, testing for accuracy issues, and being a great community resource.  Also thanks to [Colblitz](https://github.com/colblitz) for helping me find several gameplay formulas I was missing.  Additionally, thanks to Byungshin for helping me nail down a few errors bugs in the gold calculations.