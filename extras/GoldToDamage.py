"""
New vs. Old Gold to Damage Formula.
By: MetxChris
Python: v3.6

** DISCLAIMER **
This only converts a gold multiplier into a damage multiplier for the
current stage that the player is on. It does not provide a general form
for damage in terms of gold, and should not be used in any optimizers.

Instructions:
Change the user inputs for (g, L, a) below and then run the code.

Table of values for a:
Hero levels 0 to 10,       a = 1.0718
Hero levels 10 to 90,      a = 1.0353
Hero levels 90 to 370,     a = 1.0586
Hero levels 370 to 999,    a = 1.0384
Hero levels 1000 to 1999,  a = 1.0572
Hero levels 2000 to 4000,  a = 1.0504
Hero levels 4000 to 6000,  a = 1.0321
"""
# User Inputs:
g = 1 # Additional Gold Multiplier
L = 1320 # Strongest Hero Level


# I used these with the plot_d() function.
# max_exponent, L = 10.68, 90 #L = 90 to 370
# max_exponent, L = 22.85, 370 #L = 370 to 970
# max_exponent, L = 12.2, 1000 #L = 1000 to 1320
# max_exponent, L = 24.37, 1320 #L = 1320 to 1960
# max_exponent, L = 76.08, 2000 #L = 2000 to 4000
# max_exponent, L = 76.08, 4000 #L = 4000 to 6000
# max_exponent, L = 76.08/2, 6000 #L = 6000 to 7000

# max_exponent, L = 36.53, 1000 #L = 1000 to 1960

# Hero Upgrade Base (from the game-code)
b = 1.082

import math

# Levels Purchased (original formula)
def n_old(g, L):
    return round(math.log(1+g*(1-b**(-1)))/math.log(b), 2)

# Levels Purchased (updated formula)
def n(g, L):
    return round(math.log(1+(g-1)*(1-b**(-L)))/math.log(b), 2)

# Equivalent Damage Multiplier
def d(n, L, a):
    return round(a**n * (L+n)/L, 2)

# Smoothed Bonus Damage Multiplier
def a(L):

    def a_mult(mult_i, mult_f, level_i, level_f):
        mult_ratio = mult_f/mult_i
        level_diff = level_f - level_i
        return mult_ratio**(1/level_diff)

    if L>=1 and L<10:
        multiplier = a_mult(1, 2, 1, 10)
    elif L>=10 and L<90:
        multiplier = a_mult(2, 32, 10, 90)
    elif L>=90 and L<370:
        multiplier = a_mult(32, 2.72*10**8, 90, 370)
    elif L>=370 and L<970:
        multiplier = a_mult(2.72*10**8, 5.33*10**18, 370, 970)
    elif L>=970 and L<1000:
        multiplier = 0.
        #a_mult(5.33*10**18, 5.33*10**20, 970, 1000)
    elif L>=1000 and L<1320:
        multiplier = a_mult(5.33*10**20, 3.69E+28, 1000, 1320)
        # multiplier = a_mult(3.69E+28, 7.24*10**44, 1320, 1960)
    elif L>=1320 and L<1960:
        multiplier = a_mult(3.69E+28, 7.24*10**44, 1320, 1960)
        # multiplier = a_mult(5.33*10**20, 7.24*10**44, 1000, 1960)
    elif L>=1960 and L<2000:
        multiplier = 0.
        #a_mult(7.24*10**44, 7.24*10**46, 1960, 2000)
    elif L>=2000 and L<4000:
        multiplier = a_mult(7.24*10**46, 3.44*10**89, 2000, 4000)
    elif L>=4000 and L<6000:
        multiplier = a_mult(3.44*10**89, 9.03*10**116, 4000, 6000)
    else:
        multiplier = 1.
    return multiplier

def print_comparison(g, L):
    if a(L) == 0:
        print('Unsupported value for L =', L)
    else:
      print('Inputs:',
          '\n\tAdditional Gold Mult., g =', g,
          '\n\tStrongest Hero Level,  L =', L,
          '\n\tSmoothed Bonus Mult.,  a =', round(a(L), 4))
      print('\nNew Formula:')
      print('\tAdditional Hero Levels,  n = '+str(n(g, L)),
          '\n\tEquivalent Damage Mult., d = '+str(d(n(g, L), L, a(L))))
      print('\nOld Formula:')
      print('\tAdditional Hero Levels,  n = '+str(n_old(g, L)),
          '\n\tEquivalent Damage Mult., d = '+str(d(n_old(g, L), L, a(L))))

def plot_d(g_range, d_range):
    import numpy as np
    import matplotlib.pyplot as plt

    g = g_range
    d = d_range
    slope, intercept = np.polyfit(np.log10(g), np.log10(d), 1)
    fit = 10**(np.log10(g)*slope)# + intercept
    fig = plt.figure(figsize=(6, 4.5))
    xa, ya = 1.1, 1
    ax = fig.add_subplot(111, 
        xlim=(min(g)/xa, xa*max(g)),
        ylim=(min(d)/ya, ya*max(d)))
    ax.set_xlabel('Gold Multiplier', fontsize=11)
    ax.set_ylabel('Damage Multiplier', fontsize=11)
    ax.set_title('Damage vs. Gold Multiplier,   L = '+str(L)+' to '+str(L+int(n(g[-1], L))),
        fontsize=13, loc=('center'))
    ax.loglog(g, d,
        'o',markersize=5, markeredgewidth=2, color='b',
        fillstyle='none', label='Damage Multiplier')
    ax.loglog(g, fit,
        '--',markersize=3, markeredgewidth=0.5, color='r',
        fillstyle='none', label='$d = g^{'+str('%.4f'%slope)+'}$')
    # ax.plot(np.log10(g), np.log10(d),
    #     'o',markersize=5, markeredgewidth=2, color='b',
    #     fillstyle='none', label='Damage Multiplier')
    # ax.loglog(np.log10(g), fit,
    #     '--',markersize=3, markeredgewidth=0.5, color='r',
    #     fillstyle='none', label='y = '+str(round(slope, 4))+'x + '+str(round(intercept, 4)))
    legend = ax.legend(loc='upper left', frameon=False, fontsize=11)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    import numpy as np
    print_comparison(g, L)

    # d_range = np.zeros(10)
    # g_range = g*10.**np.arange(0, max_exponent, max_exponent/10)
    # for i, g_value in enumerate(g_range):
    #     d_range[i] = d(n(g_value, L), L, a(L))

    # plot_d(g_range, d_range)