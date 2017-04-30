"""
TitanHP vs CritChance Aura Comparison
by MetxChris
Python: v3.6

The equations for n, d, and a were taken from my post on gold to 
damage multiplier conversion:
https://www.reddit.com/r/TapTitans2/comments/668gdl/math_deriving_a_gold_to_damage_multiplier_formula/
"""

#Aura Values
titan_hp_aura = 0.29
crit_chance_aura = 14

#Critical Hit Stats (Read from Stats Window)
crit_chance = 10.2
crit_min = 22.0
crit_max = 198.0

#Hero Levels to Use in Calculations
#Currently no support for levels 970-999 and 1960-1999
level_range = [10, 90, 370, 1000, 2000, 4000, 6000]

#Hero Upgrade Base (hard-coded)
b = 1.082

import math

# Hero Levels Purchased
def n(g, L):
    return round(math.log(1+(g-1)*(1-b**(-L)))/math.log(b), 2)

# Equivalent Damage Multiplier
def d(n, L, a):
    return a**n*(1 + n/L)

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
    elif L>=1000 and L<1960:
      multiplier = a_mult(5.33*10**20, 7.24*10**44, 1000, 1960)
    elif L>=1960 and L<2000:
      multiplier = 0.
    elif L>=2000 and L<4000:
      multiplier = a_mult(7.24*10**46, 3.44*10**89, 2000, 4000)
    elif L>=4000 and L<6000:
      multiplier = a_mult(3.44*10**89, 9.03*10**116, 4000, 6000)
    else:
      multiplier = 1.
    return multiplier
    
# Used in Pet Damage Calculation
def crit_bonus(crit_chance):
  crit_probability = min(crit_chance, 50)/100
  return 1 + crit_probability*(crit_min + crit_max)/2
  
# Convert HP Aura to Damage Multiplier
def hp_aura_to_damage(titan_hp_aura, L):
  return d(n(titan_hp_aura, L), L, a(L))/titan_hp_aura

hline = '-'*(23)
print('Input Values:')
print(hline)
print('Crit Chance Aura:'.ljust(18), 
    str(crit_chance_aura).rjust(4),
    '\n'+'Titan HP Aura:'.ljust(18), 
    str(titan_hp_aura).rjust(4))
print(hline)
print('Crit Chance:'.ljust(17), str(crit_chance).rjust(5),
    '\n'+'Crit Min:'.ljust(17), str(crit_min).rjust(5),
    '\n'+'Crit Max:'.ljust(17), str(crit_max).rjust(5))
print(hline)

hline = '-'*(14+16+18)
print('\nEquivalent Damage Multipliers:')
print(hline)
print('Hero Level'.ljust(14), 
    'Titan HP Aura'.ljust(16),
    'Crit Chance Aura'.ljust(18))
print(hline)
for level in level_range:
    crit_ratio = crit_bonus(crit_chance+crit_chance_aura)/crit_bonus(crit_chance)
    print(str(level).rjust(10),
        str('%.2f'%hp_aura_to_damage(titan_hp_aura, level)).rjust(17),
        str(round(crit_ratio,2)).rjust(19))
print(hline)