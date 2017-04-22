from __future__ import division, print_function
import numpy as np
from Classes import GameData, notate
from ServerVarsModel import SVM
import matplotlib.pyplot as plt

"""
The plotting functions aren't as well kept as the main simulation, yet.
"""

def dps_vs_bosshp(player, stage):
    
    domain = player.total_dps_array[:, 0]>0
    x = stage.number[domain][::5]
    y1 = player.total_dps_array[:, 0][domain][::5]
    y2 = stage.boss_hp[domain][::5]
    fig = plt.figure(figsize=(0.75*6, 0.75*4.5))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(np.minimum(y1, y2).min(), np.maximum(y1, y2).max()))
    ax.set_xlabel('Stage Number', fontsize=10)
    ax.set_ylabel('Amount', fontsize=10)
    ax.set_title('DPS and Boss HP vs. Stage',
        fontsize=11, loc=('center'))
    ax.semilogy(x, y1,
        'o',markersize=3, markeredgewidth=0.75, color='b',
        fillstyle='none', label='Total DPS')
    ax.plot(x, y2,
        'x',markersize=3, markeredgewidth=0.75, color='r',
        fillstyle='none', label='Boss HP')
    legend = ax.legend(loc='upper left', frameon=False)
    plt.tight_layout()
    plt.show()

def tap_damage(player, stage):
    domain1 = player.tap_damage_array[:, 0]>0
    domain2 = player.tap_damage_array[:, 1]>0
    x1 = stage.number[domain1][::5]
    x2 = stage.number[domain2][::5]
    y1 = player.tap_damage_array[:, 0][domain1][::5]
    y2 = player.tap_damage_array[:, 1][domain2][::5]
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x1), max(x1)),
        ylim=(min(y1), max(y1)))
    ax.set_xlabel('Stage', fontsize=10)
    ax.set_ylabel('Damage', fontsize=10)
    ax.set_title('Tap Damage Comparison',
        fontsize=11, loc=('center'))
    ax.semilogy(x1, y1,
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
    y1 = player.tap_dps_array[domain][::5]
    y2 = player.hero_dps_array[domain][::5]
    y3 = pet_dps_array[domain][::5]
    y4 = player.gold_array[domain][::5].sum(axis=1)

    fig = plt.figure(figsize=(0.75*6, 0.75*4.5))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(min(y1), max(y4)))
    ax.set_xlabel('$\\rm Stage$', fontsize=10)
    ax.set_ylabel('Amount', fontsize=10)
    ax.set_title('DPS Type and Gold Comparison at '+tap_rate+' taps/s',
        fontsize=11, loc=('center'))
    ax.semilogy(x, y1, '-',
        markersize=3, 
        markeredgewidth=0.75, 
        color='b',
        fillstyle='none', 
        label='Tap DPS')
    ax.plot(x, y2, '--',
        markersize=3, 
        markeredgewidth=0.5, 
        color='r',
        fillstyle='none', 
        label='Hero DPS')
    ax.plot(x, y3, '-.',
        markersize=3, 
        markeredgewidth=0.5, 
        color='g',
        fillstyle='none', 
        label='Pet DPS')
    ax.plot(x, y4, ':',
        markersize=3, 
        markeredgewidth=0.5, 
        color='m',
        fillstyle='none', 
        label='Gold')
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

    domain = player.relic_efficiency[0, :]>0
    x = stage.number[domain]
    y1 = player.relic_efficiency[4, domain]
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(min(y1[10:]), 1.01*max(y1)))
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('${\\rm Relic\ Efficiency}$', fontsize=10)
    max_efficiency = y1.max()
    max_efficiency_stage = y1.argmax() + 2 + player.start_stage
    title = ('Most Efficient Stage: '
        + str(max_efficiency_stage)+','
        + '  Efficiency: '+ str(round(max_efficiency, 2)))
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.plot(x, y1, '-', markersize=2, markeredgewidth=0.5, color='b',
        fillstyle='none', label=str(player.attack_durations[4])+'s interval')
    legend = ax.legend(loc='best', frameon=False, fontsize=9)
    plt.tight_layout()
    plt.show()

def time_per_stage(player, stage):
    # self.attack_durations must have at least 5 elements for this to work.
    domain = player.active_time[0, :]>0
    i1 = 4
    x = stage.number[domain]
    y1 = player.active_time[i1, :][domain] + player.wasted_time[i1, :][domain]
    sec60 = 60*np.ones_like(x)
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(min(1, y1.min()), max(y1)))
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('Time (s)', fontsize=10)
    title = 'Time Per Stage'
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.semilogy(x, y1, '-', markersize=2, markeredgewidth=0.75, color='b',
        fillstyle='none', label=str(player.attack_durations[i1])+'s interval')
    ax.plot(x, sec60, ':', markersize=2, markeredgewidth=0.75, color='k',
        fillstyle='none', label='60 seconds')
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

    def moving_average (values, window):
        weights = np.repeat(1.0, window)/window
        return np.convolve(values, weights, 'valid')

    y1 = moving_average(player.regen_performance[idx, :][domain], 5)
    minY, maxY = y1.min(), y1.max()
    if siphon_exists:
        y2 = player.siphon_performance[idx, :][domain][4:]
        minY = min(minY, y2.min())
        maxY = max(maxY, y2.max())
    if manni_exists:
        y3 = player.manni_performance[idx, :][domain][4:]
        minY = min(minY, y3.min())
        maxY = max(maxY, y3.max())
    fig = plt.figure(figsize=(6*0.75, 4.5*0.75))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(0.99*minY, 1.01*maxY))
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('Mana', fontsize=10)
    title = 'Mana Gain Per Stage, Interval: '+str(player.attack_durations[idx])+'s'
    ax.set_title(title, fontsize=11, loc=('center'))
    ax.semilogy(x, y1, 'o', markersize=3, markeredgewidth=0.75, color='b',
        fillstyle='none', label='Mana Regen (5-stage avg)')
    if siphon_exists:
        ax.plot(x, y2, 'x', markersize=3, markeredgewidth=0.75, color='r',
            fillstyle='none', label='Mana Siphon ('+str(int(player.taps_sec))+' taps/s)')
    if manni_exists:
        ax.plot(x, y3, '*', markersize=3, markeredgewidth=0.75,color='g',
            fillstyle='none', label='Manni Mana (avg)')
    legend = ax.legend(loc='best', frameon=False, fontsize=10)
    plt.tight_layout()
    plt.show()