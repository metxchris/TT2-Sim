from __future__ import division, print_function
import numpy as np
from Classes import GameData, letters
from ServerVarsModel import SVM
import matplotlib.pyplot as plt

"""
The plotting functions aren't as well kept as the main simulation, yet.
"""

def dps_vs_bosshp(player, stage):
    
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

def tap_damage(player, stage):
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

def dps_vs_gold(player, stage):
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

def splash(player, stage, max_splash=20):
    """ Bounds on x auto-adjust to where all the action is. """

    domain = player.total_dps_array[:, 0]>0
    x = stage.number[domain][1:]
    y1 = np.minimum(player.splash_array[domain][1:], max_splash)
    # Build floor Splash array.
    y2 = np.zeros_like(y1)
    y2[0] = y1[0]
    for i in range(1, y1.size):
        y2[i] = min(y2[i-1], y1[i])
    # Determine nice bounds on x.
    start = max(stage.number[domain][1:][y2==y2.max()].argmax()-20, 0)
    end = min(stage.number[domain][1:][y1>0].max()+10, 
                stage.number[domain][-1])-stage.number[domain][1]

    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(x[start], x[end]),
        ylim=(0, (max(y1)+1)))

    #yint = range(int(min(y)), int(max(y))+1, int(max(y)/10))
    #plt.yticks(yint)
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('${\\rm Amount\ Splashed}$', fontsize=10)
    title='Splash from Stages '+str(min(x)-1)+' to '+str(max(x))
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.plot(x, y1, 'o', markersize=3, markeredgewidth=0.75, color='b',
        fillstyle='none', label='Max')
    ax.plot(x, y2, '-', markersize=3, linewidth=1.25, color='r',
        fillstyle='none', label='Floor')
    legend = ax.legend(loc='best', frameon=False)
    plt.tight_layout()
    plt.show()

def relic_efficiency(player, stage):
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

def time_per_stage(player, stage):
    # self.attack_durations must have at least 5 elements for this to work.
    domain = player.active_time[0, :]>0
    x = stage.number[domain]
    i1, i2, i3 = 4, -2, -1
    y1 = player.active_time[i1, :][domain] + player.wasted_time[i1, :][domain]
    y2 = player.active_time[i2, :][domain] + player.wasted_time[i2, :][domain]
    y3 = player.active_time[i3, :][domain] + player.wasted_time[i3, :][domain]
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(min(y1), max(y1.max(), y2.max(), y3.max())))
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('Time (s)', fontsize=10)
    max_efficiency = letters(max(player.relic_efficiency[:, 0]))
    title = 'Time Per Stage'
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.plot(x, y1, 'o', markersize=2, markeredgewidth=0.75, color='b',
        fillstyle='none', label=str(player.attack_durations[i1])+'s interval')
    ax.plot(x, y2, 'x', markersize=2, markeredgewidth=0.5, color='r',
        fillstyle='none', label=str(player.attack_durations[i2])+'s interval')
    # ax.plot(x, y3, ':', linewidth=1.25, color='g',
    #     fillstyle='none', label=str(player.attack_durations[i3])+'s interval')
    legend = ax.legend(loc='upper left', frameon=False, fontsize=9)
    plt.tight_layout()
    plt.show()

def mana_regen_per_stage(player, stage):
    # self.attack_durations must have at least 5 elements for this to work.
    idx = 4
    domain = player.wasted_time[idx, :]>0
    siphon_exists = player.mana_siphon
    manni_exists = player.manni_mana
    x = stage.number[domain][4:]

    def movingaverage (values, window):
        weights = np.repeat(1.0, window)/window
        return np.convolve(values, weights, 'valid')

    y1 = movingaverage(player.regen_performance[idx, :][domain], 5)
    if siphon_exists:
        y2 = player.siphon_performance[idx, :][domain][4:]
    if manni_exists:
        y3 = player.manni_performance[idx, :][domain][4:]
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(0.99*min(y1.min(), y2.min(), y3.min()), 1.01*max(y1.max(), y2.max(), y3.max())))
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('Mana', fontsize=10)
    title = 'Mana Gain Per Stage, Interval: '+str(player.attack_durations[idx])+'s'
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.plot(x, y1, 'o', markersize=2, markeredgewidth=0.75, color='b',
        fillstyle='none', label='Mana Regen (5-stage avg)')
    if siphon_exists:
        ax.plot(x, y2, 'x', markersize=2, markeredgewidth=0.5, color='r',
            fillstyle='none', label='Mana Siphon ('+str(int(player.taps_sec))+' taps/s)')
    if manni_exists:
        ax.plot(x, y3, '*', markersize=2, markeredgewidth=0.5,color='g',
            fillstyle='none', label='Manni Mana (avg)')
    legend = ax.legend(loc='best', frameon=False, fontsize=9)
    plt.tight_layout()
    plt.show()