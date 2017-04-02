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
    fig = plt.figure(figsize=(6, 4.5))
    ax = fig.add_subplot(111, 
        xlim=(min(x), max(x)),
        ylim=(0, (max(y1)+1)))
    yint = range(min(y1), max(y1)+1, 2)
    plt.yticks(yint)
    ax.set_xlabel('$\\rm Stage\ Number$', fontsize=12)
    ax.set_ylabel('${\\rm Amount\ Splashed}=n_{\\rm s}$', fontsize=12)
    t1='$n_{\\rm s} = \max\{n\geq 0\}\qquad {\\rm for}\qquad'
    t2='D_{\\rm splash}\geq n\cdot y^{n-1}\cdot H_{\\rm titan}$'
    ax.set_title(t1+t2, fontsize=12, loc=('center'))
    ax.plot(x, y1, 'o', markersize=3, markeredgewidth=0.5, color='b',
        fillstyle='none', label='$y = 1, {\\rm\ (default)}$')
    ax.plot(x, y2, 'x', markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='$y = 2$')
    legend = ax.legend(loc='lower left', frameon=False)
    plt.tight_layout()
    plt.show()
