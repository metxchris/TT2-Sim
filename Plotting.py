from __future__ import division, print_function
import numpy as np
from Classes import GameData, letters
from ServerVarsModel import SVM
import matplotlib.pyplot as plt

"""
The plotting functions aren't as well kept as the main simulation, 
and some may break as I continue to make changes.
"""

def plot_dps_vs_bosshp(player, stage):
    
    domain = player.total_dps_array[:, 0]>0
    x = stage.number[domain][::5]
    y1 = np.log(player.total_dps_array[:, 0][domain][::5])
    y2 = np.log(stage.boss_hp[domain][::5])
    fig = plt.figure(figsize=(0.75*6, 0.75*4.5))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(np.minimum(y1, y2).min(), np.maximum(y1, y2).max()))
    ax.set_xlabel('$\\rm Stage Number$', fontsize=10)
    ax.set_ylabel('$\\rm \log{(Amount)}$', fontsize=10)
    ax.set_title('$\\rm \log{(Total\ DPS)}\ vs. \log{(Boss\ HP)}$',
        fontsize=11, loc=('center'))
    ax.plot(x, y1,
        'o',markersize=3, markeredgewidth=0.5, color='b',
        fillstyle='none', label='Total DPS')
    ax.plot(x, y2,
        'x',markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='Boss HP')
    legend = ax.legend(loc='upper left', frameon=False)
    plt.tight_layout()
    plt.show()

def plot_tap_damage(player, stage):
    domain1 = player.tap_damage_array[:, 0]>0
    domain2 = player.tap_damage_array[:, 1]>0
    x1 = stage.number[domain1][::5]
    x2 = stage.number[domain2][::5]
    y1 = np.log(player.tap_damage_array[:, 0][domain1][::5])
    y2 = np.log(player.tap_damage_array[:, 1][domain2][::5])
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x1), max(x1)),
        ylim=(min(y1), max(y1)))
    ax.set_xlabel('$\\rm Stage$', fontsize=10)
    ax.set_ylabel('$\\rm \log{(Damage)}$', fontsize=10)
    ax.set_title('$\\rm Tap\ Damage\ Comparison$',
        fontsize=11, loc=('center'))
    ax.plot(x1, y1,
        'o',markersize=3, markeredgewidth=0.75, color='b',
        fillstyle='none', label='Sword Master + Tap from Heroes')
    ax.plot(x2, y2,
        'x',markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='Sword Master Only')
    legend = ax.legend(loc='upper left', frameon=False)
    plt.tight_layout()
    plt.show()

def plot_dps(player, stage):
    pet_dps_array = player.pet_attack_damage_array*player.pet_rate
    tap_rate = str(player.taps_sec)

    domain = player.total_dps_array[:, 0]>0
    x = stage.number[domain][::5]
    y1 = np.log(player.tap_dps_array[domain][::5])
    y2 = np.log(player.hero_dps_array[domain][::5])
    y3 = np.log(pet_dps_array[domain][::5])
    y4 = np.log(player.gold_array[domain][::5].sum(axis=1))

    fig = plt.figure(figsize=(0.75*6, 0.75*4.5))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(min(y1), max(y4)))
    ax.set_xlabel('$\\rm Stage$', fontsize=10)
    ax.set_ylabel('$\\rm \log{(DPS)}$', fontsize=10)
    ax.set_title('DPS Type and Gold Comparison at '+tap_rate+' taps/s',
        fontsize=11, loc=('center'))
    ax.plot(x, y1, '-',markersize=3, markeredgewidth=0.75, color='b',
        fillstyle='none', label='Tap DPS')
    ax.plot(x, y2, '--',markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='Hero DPS')
    ax.plot(x, y3, '-.',markersize=3, markeredgewidth=0.5, color='g',
        fillstyle='none', label='Pet DPS')
    ax.plot(x, y4, ':',markersize=3, markeredgewidth=0.5, color='m',
        fillstyle='none', label='Gold')
    legend = ax.legend(loc='upper left', frameon=False, fontsize=9)
    plt.tight_layout()
    plt.show()

def plot_splash(player, stage, max_splash=20):
    """ You may want to adjust your starting stage to get a nice plot here. """

    domain = player.splash_array>0
    x = stage.number[domain]
    y = np.minimum(player.splash_array[domain], max_splash)
    # Build Cont. Splash array.
    y2 = np.zeros_like(y)
    y2[0] = y[0]
    for i in range(1, y.size):
        y2[i] = min(y2[i-1], y[i])

    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(0, (max(y)+1)))
    #yint = range(int(min(y)), int(max(y))+1, int(max(y)/10))
    #plt.yticks(yint)
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('${\\rm Amount\ Splashed}$', fontsize=10)
    title='Splash from Stages '+str(min(x))+' to '+str(max(x))
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.plot(x, y, 'o', markersize=3, markeredgewidth=0.75, color='b',
        fillstyle='none', label='Max Splash')
    ax.plot(x, y2, '-', markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='Cont. Splash')
    legend = ax.legend(loc='lower left', frameon=False)
    plt.tight_layout()
    plt.show()

def plot_relics(player, stage):
    """ This calc isn't finished yet. """

    domain = player.relic_efficiency[:, 0]>0
    x = stage.number[domain]
    y = player.relic_efficiency[:, 0][domain]
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(min(y[10:]), 1.1*max(y)))
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('${\\rm Relic\ Efficiency}$', fontsize=10)
    max_efficiency = letters(max(player.relic_efficiency[:, 0]))
    title = ('Most Efficient Stage: '
        + str((player.relic_efficiency[:, 0]).argmax())
        + '     Efficiency: '+ max_efficiency)
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.plot(x, y, 'o', markersize=2, markeredgewidth=0.5, color='b',
        fillstyle='none')
    plt.tight_layout()
    plt.show()