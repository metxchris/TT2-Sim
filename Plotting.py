from __future__ import division, print_function
import numpy as np
from Classes import GameData, letters
from ServerVarsModel import SVM

def plot_results(player, stage):
    import matplotlib.pyplot as plt
    indices = player.total_dps_array>0
    fig = plt.figure(figsize=(6, 4.5))
    ax = fig.add_subplot(111, 
        xlim=(min(stage.number[indices]), max(stage.number[indices])),
        ylim=(min(np.log(stage.boss_hp[indices])), max(np.log(stage.boss_hp[indices]))))
    ax.set_xlabel('$\\rm Stage Number$', fontsize=12)
    ax.set_ylabel('$\\rm \log{(Amount)}$', fontsize=12)
    ax.set_title('$\\rm \log{(Total\ DPS)}\ vs. \log{(Boss\ HP)}$',
        fontsize=14, loc=('center'))
    ax.plot(stage.number[indices][::5], np.log(player.total_dps_array[indices][::5]),
        'o',markersize=3, markeredgewidth=0.5, color='b',
        fillstyle='none', label='Total DPS')
    ax.plot(stage.number[indices][::5], np.log(stage.boss_hp[indices][::5]),
        'x',markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='Boss HP')
    legend = ax.legend(loc='upper left', frameon=False)
    plt.tight_layout()
    plt.show()

def plot_splash(player, stage):
    import matplotlib.pyplot as plt
    domain = player.total_dps_array>0
    x = stage.number[domain]
    y1 = player.splash_array[domain]
    y2 = player.splash_array_penalty[domain]
    fig = plt.figure(figsize=(6*0.8, 4.5*0.8))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(0, (max(y1)+1)))
    yint = range(min(y1), max(y1)+1, 2)
    plt.yticks(yint)
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=10)
    ax.set_ylabel('${\\rm Amount\ Splashed}$', fontsize=10)
    title='Splash Comparison from Stages '+str(min(x))+' to '+str(max(x))
    ax.set_title(title, fontsize=10, loc=('center'))
    ax.plot(x, y1, 'o', markersize=3, markeredgewidth=0.75, color='b',
        fillstyle='none', label='$y = 1}$')
    ax.plot(x, y2, 'x', markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='$y = 1+ {\\rm floor}\\left (\\frac{\\rm stage}{1000}\\right )$')
    legend = ax.legend(loc='lower left', frameon=False)
    plt.tight_layout()
    plt.show()

def plot_splash_compare(player, player2, stage):
    import matplotlib.pyplot as plt
    domain = player.total_dps_array>0
    x = stage.number[domain]
    y1 = player.splash_array[domain]
    y2 = player2.splash_array[domain]
    fig = plt.figure(figsize=(6*0.9, 4.5*0.9))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(0, (max(y1)+1)))
    yint = range(min(y1), max(y1)+1, 2)
    plt.yticks(yint)
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=12)
    ax.set_ylabel('${\\rm Amount\ Splashed}$', fontsize=12)
    title='Splash Comparison up to +20 kills, with Kit = 0'
    ax.set_title(title, fontsize=12, loc=('center'))
    ax.plot(x, y1, 'o', markersize=4, markeredgewidth=0.5, color='b',
        fillstyle='none', label='Extended Reach = 1')
    ax.plot(x, y2, 'x', markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='Extended Reach = 20')
    legend = ax.legend(loc='lower left', frameon=False)
    plt.tight_layout()
    plt.show()
