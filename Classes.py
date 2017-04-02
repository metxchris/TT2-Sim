from __future__ import division, print_function
import numpy as np
from copy import deepcopy
from math import modf
from ServerVarsModel import SVM

  
class GameData(object):
    def __init__(self, input_file):
        self.input = np.genfromtxt('player\\'+input_file, delimiter=',', dtype=np.string_)
        self.active_skills = ActiveSkills(self.input)
        self.artifacts = Artifacts(self.input)
        self.equipment = Equipment(self.input)
        self.heroes = Heroes(self.input)
        self.hero_multipliers = HeroMultipliers(self.heroes.level.size)
        self.hero_skills = HeroSkills(self.heroes.id.size)
        self.pets = Pets(self.input)
        self.skill_tree = SkillTree(self.input)
        self.stage = Stage(self.input, self.skill_tree, self.equipment.titan_hp)

    def print_info(self, stage_skip_factor=100):
        self.artifacts.print_info()
        self.equipment.print_info()
        self.heroes.print_info()
        self.pets.print_info()
        self.skill_tree.print_info()
        self.stage.print_info(stage_skip_factor)
    

class ActiveSkills(object):
    def __init__(self, input_csv):
        csv_data = np.genfromtxt('csv\ActiveSkills.csv',
            delimiter=',', dtype=np.string_)

        # Find active skill info in player input CSV.
        start_idx = np.array([input_csv[:,0]=='ACTIVE SKILL LEVELS']).argmax()+1
        end_idx = start_idx + 6
        skill_levels = input_csv[start_idx:end_idx,0].astype(np.int)
        types = input_csv[start_idx:end_idx, 1]
        active = (input_csv[start_idx:end_idx, 2]!='')

        z = np.array([0])
        cs_skill = max(z, skill_levels[(types=='CriticalStrike')*active])[0]+1
        hom_skill = max(z, skill_levels[(types=='HandOfMidas')*active])[0]+1
        wc_skill = max(z, skill_levels[(types=='WarCry')*active])[0]+1

        self.crit_strike = csv_data[cs_skill, 2].astype(np.float)
        self.hom = csv_data[hom_skill, 3].astype(np.float)
        self.war_cry = csv_data[wc_skill, 5].astype(np.float)


class Artifacts(object):
    def __init__(self, input_csv):
        artifacts = np.genfromtxt('csv\ArtifactInfo.csv', 
            delimiter=',', dtype=np.string_)

        # Find artifact info in player input CSV.
        start_idx = np.array([input_csv[:,0]=='ARTIFACT LEVELS']).argmax()+1
        end_idx = start_idx + artifacts[1:,0].size

        self.id = artifacts[1:,0]
        self.name = artifacts[1:,9]
        self.max_level = artifacts[1:,1].astype(np.int)
        self.type = artifacts[1:,3]
        self.effect_inc = artifacts[1:,4].astype(np.float)
        self.damage_inc = artifacts[1:,5].astype(np.float)

        # Set artifact effects and damages based on player artifact levels.
        self.level = input_csv[start_idx:end_idx, 0].astype(np.int)
        self.effect = self.effect_inc*self.level
        self.damage = self.damage_inc*self.level

        # Add base level to effect multipliers where needed.
        artifact_names = (['Furies Bow', 'Heavenly Sword', 'Fruit of Eden', 
            'Charm of the Ancient', 'The Sword of Storms', 'Book of Prophecy',
            'Drunken Hammer', 'Divine Retribution', 'Laborer\'s Pendant',
            'Blade of Damocles', 'Parchment of Foresight', 'Heroic Shield',
            'Stone of the Valrunes', 'Elixir of Eden', 'Bringer of Ragnarok',
            'Titan\'s Mask', 'Chest of Contentment', 'Hero\'s Blade',
            'Helmet of Madness', 'Lethe Water', 'Amethyst Staff'])
        for name in artifact_names:
            self.effect[self.name==name] += 1

        # Total artifact damage bonus.
        self.total_damage = ((1+np.sum(self.damage))
            * self.effect[self.name=='Heavenly Sword'][0])

    def print_info(self):
        print('')
        print('ARTIFACT NAME'.ljust(22), '\t'+'LEVEL'.rjust(5),
            '\t'+'EFFECT'.rjust(6), '\t'+'DAMAGE'.rjust(8))
        for i, name in enumerate(self.name):
            if (self.level[i]==0):
                continue
            print(name.ljust(22), '\t'+str(self.level[i]).rjust(5), 
                '\t'+str('%.2f'%self.effect[i]).rjust(6), 
                '\t'+letters(self.damage[i], '%').rjust(8))
        print('Total Artifact Damage:', letters(self.total_damage, '%'))


class Equipment(object):
    def __init__(self, input_csv):
        start_idx = np.array([input_csv[:,0]=='EQUIPMENT MULTIPLIERS']).argmax()+1
        end_idx = start_idx + np.array([input_csv[start_idx:,0]=='']).argmax()
        types = input_csv[start_idx:end_idx, 1]
        effects = input_csv[start_idx:end_idx, 0].astype(np.float)
        equipped = (input_csv[start_idx:end_idx, 2]!='')

        # Initialize default Values
        a, b = (np.array([0]), np.array([1]))
        self.melee_mult = max(b, effects[(types=='MeleeDamage')*equipped])[0]
        self.ranged_mult = max(b, effects[(types=='RangedDamage')*equipped])[0]
        self.spell_mult = max(b, effects[(types=='SpellDamage')*equipped])[0]
        self.all_gold = max(b, effects[(types=='AllGold')*equipped])[0]
        self.chest_gold = max(b, effects[(types=='ChestGold')*equipped])[0]
        self.chest_chance = max(a, effects[(types=='ChestChance')*equipped])[0]
        self.all_hero_damage = max(b, effects[(types=='AllHeroDamage')*equipped])[0]
        self.all_damage = max(b, effects[(types=='AllDamage')*equipped])[0]
        self.pet_mult = max(b, effects[(types=='PetDamage')*equipped])[0]
        self.crit_damage = max(b, effects[(types=='CritDamage')*equipped])[0]
        self.crit_chance = max(a, effects[(types=='CritChance')*equipped])[0]
        self.titan_hp = min(b, effects[(types=='TitanHP')*equipped])[0]
        self.tap_damage = max(b, effects[(types=='TapDamage')*equipped])[0]

    def print_info(self):
        names = (['Sword', 'Sword', 'Sword', 'Helmet', 'Helmet', 'Helmet',
            'Armor', 'Armor', 'Aura', 'Aura', 'Aura', 'Slash', 'Slash'])
        types = (['AllDamage', 'AllHeroDamage', 'CritDamage', 'MeleeDamage',
            'SpellDamage', 'RangedDamage', 'AllGold', 'ChestGold', 'CritChance',
            'ChestChance', 'TitanHP', 'PetDamage', 'TapDamage'])
        effects = ([self.all_damage, self.all_hero_damage, self.crit_damage, 
            self.melee_mult, self.spell_mult, self.ranged_mult,
            self.all_gold, self.chest_gold, self.crit_chance, self.chest_chance,
            self.titan_hp, self.pet_mult, self.tap_damage])

        print('')
        print('EQUIPMENT'.ljust(10), '\t'+'TYPE'.ljust(13), '\t'+'EFFECT'.rjust(6))
        for i, j in enumerate(types):
            if (effects[i]==1 or effects[i]==0):
                continue
            print(names[i].ljust(10), '\t'+types[i].ljust(13),
                '\t'+str(effects[i]).rjust(6))


class Heroes(object):
    def __init__(self, input_csv):
        # Read CSV Files.
        helper_info = np.genfromtxt('csv\HelperInfo.csv', 
            delimiter=',', dtype=np.string_)
        id_size = helper_info[1:,0].size

        # Weapon level location in player input CSV.
        start_idx = np.array([input_csv[:,0]=='HERO WEAPON LEVELS']).argmax()+1
        end_idx = start_idx + id_size

        # Initialize Hero Information.
        self.id = helper_info[1:,0]
        self.name = helper_info[1:,4]
        self.unlock_order = helper_info[1:,1].astype(np.int)
        self.type = helper_info[1:,2]
        self.purchase_cost = helper_info[1:,3].astype(np.float)
        self.level = np.zeros(id_size, dtype=np.int)
        self.weapon_levels = input_csv[start_idx:end_idx, 0].astype(np.int)
        self.set_bonus = 10*(self.weapon_levels.min())

        self.melee_type = self.type=='Melee'
        self.spell_type = self.type=='Spell'
        self.ranged_type = self.type=='Ranged'

        self.melee_dps = 0
        self.spell_dps = 0
        self.ranged_dps = 0
        self.total_dps = 0
        self.level_cap = 5000 # avoid overflow errors

    def print_info(self):
        print('')
        print('HEROES: NAME'.ljust(30), '\t'+'TYPE'.ljust(10),
            '\t'+'BASE COST'.rjust(9), '\t'+'WEAPON'.rjust(6))
        for i, name in enumerate(self.name):
            print(name.ljust(30), '\t'+self.type[i].ljust(10), 
                '\t'+letters(self.purchase_cost[i]).rjust(9),
                '\t'+str(self.weapon_levels[i]).rjust(6))


class HeroMultipliers(object):
    def __init__(self, level_size):
        improvements_info = np.genfromtxt('csv\HelperImprovementsInfo.csv', 
            delimiter=',', dtype=np.string_)   
        
        self.levels = np.zeros(improvements_info[1:,0].size+2, dtype=np.int)
        self.levels[1] = 1
        self.levels[2:] = improvements_info[1:,0].astype(np.int)
        self.bonuses = np.zeros(improvements_info[1:,2].size+2)
        self.bonuses[1] = 1
        self.bonuses[2:] = improvements_info[1:,2].astype(np.float)
        self.level_tile = np.tile(self.levels, (level_size, 1))
        self.bonus_tile = np.tile(self.bonuses, (level_size, 1))


class HeroSkills(object):
    def __init__(self, id_size):
        csv_data = np.genfromtxt('csv\HelperSkillId.csv', 
            delimiter=',', dtype=np.string_)
        self.bonus_id_tile = np.tile(csv_data[1:, 1], (id_size, 1))
        self.bonus_type_tile = np.tile(csv_data[1:, 3], (id_size, 1))
        self.bonus_mult_tile = np.tile(csv_data[1:, 4].astype(np.float), (id_size, 1)) 
        self.bonus_level_tile = np.tile(csv_data[1:, 5].astype(np.int), (id_size, 1))        


class Pets(object):
    def __init__(self, input_csv):
        # Game data.
        pet_csv = np.genfromtxt('csv\PetInfo.csv', delimiter=',', dtype=np.string_)
        dmg_base = pet_csv[1:,1].astype(np.float)
        dmg_inc = pet_csv[1:,2:5].astype(np.float)
        bonus_base = pet_csv[1:,6].astype(np.float)
        bonus_inc = pet_csv[1:,7].astype(np.float)

        # Find pet info locations in player input CSV.
        start_idx = np.array([input_csv[:,0]=='PET LEVELS']).argmax()+1
        end_idx = start_idx + pet_csv[1:,1].size
        active_idx = np.array([input_csv[start_idx:end_idx,2]!='']).argmax()

        # Initialize object values.
        self.id = pet_csv[1:,0]
        self.bonus_type = pet_csv[1:,5]
        self.level = input_csv[start_idx:end_idx, 0].astype(np.int)
        self.name = input_csv[start_idx:end_idx, 1]
        self.active_name = input_csv[start_idx:end_idx, 1][active_idx]

        # Compute arrays of active values for each pet.
        self.active_damage = (dmg_base + np.minimum(self.level, 40)*dmg_inc[:,0]
            + np.maximum(np.minimum(self.level-40, 40), 0)*dmg_inc[:,1]
            + np.maximum(self.level-80, 0)*dmg_inc[:,2])
        self.active_bonus = bonus_base + self.level*bonus_inc

        # Compute arrays of passive values for each pet.
        self.passive_factor = np.minimum(0.05*np.floor(self.level/5), 1)
        self.passive_bonus = (self.active_bonus-bonus_base)*self.passive_factor
        self.passive_bonus[self.passive_factor>0] += bonus_base[self.passive_factor>0]
        self.passive_damage = self.active_damage*self.passive_factor

        # Compute total bonus multipliers based on active pet.
        active_idx = (self.name==self.active_name)
        self.bonus_multipliers = deepcopy(self.passive_bonus)
        self.bonus_multipliers[active_idx] = self.active_bonus[active_idx]
        #self.bonus_multipliers[:-1][self.bonus_multipliers[:-1]==0] = 1

        # Compute total damage bonus based on active pet.
        self.damage_mult = (self.active_damage[self.name==self.active_name][0]
            + self.passive_damage[self.name!=self.active_name].sum() + 1)

        # Error check.
        if (self.name!=self.active_name).all():
            print('ERROR: No matches for active pet name from player input CSV.')

    def print_info(self):
        print('')
        print('PET NAME'.ljust(8), '\t'+'LEVEL'.rjust(5),
            '\t'+'P. BONUS'.rjust(8), '\t'+'P. DAMAGE'.rjust(9),
            '\t'+'A. BONUS'.rjust(8), '\t'+'A. DAMAGE'.rjust(9))
        for i, name in enumerate(self.name):
            print(name.ljust(8), '\t'+str(self.level[i]).rjust(5), 
                '\t'+str("%.3f"%self.passive_bonus[i]).rjust(8), 
                '\t'+letters(self.passive_damage[i],"%").rjust(9),  
                '\t'+str("%.2f"%self.active_bonus[i]).rjust(8),  
                '\t'+letters(self.active_damage[i],"%").rjust(9))
        print('Active Pet:', self.active_name)
        

class SkillTree(object):
    def __init__(self, input_csv):
        skill_tree = np.genfromtxt('csv\SkillTreeInfo.csv',
            delimiter=',', dtype=np.string_)
        skill_tree[skill_tree == '-'] = 'NaN' # needed for setting float type here.

        # Find skill tree info locations in player input CSV.
        start_idx = np.array([input_csv[:, 0]=='SKILL TREE LEVELS']).argmax()+1
        end_idx = start_idx + skill_tree[1:, 0].size

        self.attributes = skill_tree[1:, 0]
        self.effect_level = skill_tree[1:, 25:].astype(np.float)
        self.name = input_csv[start_idx:end_idx, 1]
        self.level = input_csv[start_idx:end_idx, 0].astype(np.int)
        self.effect = np.zeros(self.level.size)

        for i, j in enumerate(self.level):
            self.effect[i] = self.effect_level[i, self.level[i]]

    def print_info(self):
        print('')
        print('SKILL TREE: NAME'.ljust(25), '\t'+'LEVEL'.rjust(5), '\t'+'EFFECT'.rjust(6))
        for i, j in enumerate(self.level):
            if (self.level[i]==0):
                continue
            print(self.name[i].ljust(25), 
                '\t'+str(self.level[i]).rjust(5), 
                ' \t'+str(self.effect[i]).rjust(6))
        

class Stage(object):
    def __init__(self, input_csv, skill_tree, hp_multiplier):
        # Initialize Stage Information.
        stage_cap = input_csv[:, 0][input_csv[:, 1]=='StageCap'][0].astype(np.int)
        ip_level = skill_tree.effect[skill_tree.attributes=='LessMonsters'][0].astype(np.int)
        self.cap = min(stage_cap, 5500)
        self.number = np.arange(self.cap + 1)

        self.titan_hp = (SVM.monsterHPMultiplier
            * SVM.monsterHPBase1**np.minimum(self.number, SVM.monsterHPLevelOff)
            * SVM.monsterHPBase2**np.maximum(self.number-SVM.monsterHPLevelOff, 0)
            * hp_multiplier)

        self.boss_hp = (self.titan_hp
            * np.minimum(SVM.bossHPModBase**(self.number/200), 2.5))
        self.boss_hp[1::5] *= SVM.themeMultiplierSequence[0] # x1, x6 stages
        self.boss_hp[2::5] *= SVM.themeMultiplierSequence[1] # x2, x7 stages
        self.boss_hp[3::5] *= SVM.themeMultiplierSequence[2] # x3, x8 stages
        self.boss_hp[4::5] *= SVM.themeMultiplierSequence[3] # x4, x9 stages
        self.boss_hp[0::5] *= SVM.themeMultiplierSequence[4] # x5, x0 stages

        self.titan_count = np.maximum(1, 
            (10 + np.minimum(np.floor(self.number/1000)*4, 20))-ip_level).astype(np.int)

        # The player.all_gold multiplier is applied when monsters are killed.
        self.base_titan_gold = (self.titan_hp*SVM.monsterGoldMultiplier
            + SVM.monsterGoldSlope*np.minimum(self.number, SVM.noMoreMonsterGoldSlope))
        self.base_titan_gold[0] = 30 # Ensures enough starting gold to purchase first hero.
        self.base_boss_gold = (self.boss_hp*SVM.monsterGoldMultiplier
            + SVM.monsterGoldSlope*np.minimum(self.number, SVM.noMoreMonsterGoldSlope))
        self.base_boss_gold[0] = 30 # Ensures enough starting gold to purchase first hero.

    def print_info(self, stage_skip_factor=100):
        # Print to screen all values of every stage_skip_factor stages.
        print('')
        print('STAGE'.rjust(5), '\t'+'TITAN HP'.rjust(10), '\t'+'BOSS HP'.rjust(10),
            '\t'+'BASE GOLD'.rjust(10), '\t'+'TITAN #'.rjust(7))
        for i in xrange(1, int(self.cap/stage_skip_factor)+1):
            print(str(i*stage_skip_factor).rjust(5),
                '\t'+letters(self.titan_hp[i*stage_skip_factor]).rjust(10),
                '\t'+letters(self.boss_hp[i*stage_skip_factor]).rjust(10),
                '\t'+letters(self.base_titan_gold[i*stage_skip_factor]).rjust(10),
                '\t'+str(self.titan_count[i*stage_skip_factor]).rjust(7)) 


def letters(sci_number, option=''):
    """
    Input: Any number, ideally one that requires scientific notation to display.
    Returns: String in the form of ###.##aa, where aa is the associated letter pair.
    """

    number_letter_dict = ({1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g',
        8:'h', 9:'i', 10:'j', 11:'k', 12:'l', 13:'m', 14:'n', 15:'o', 16:'p',
        17:'q', 18:'r', 19:'s', 20:'t', 21:'u', 22:'v', 23:'w', 24:'x', 25:'y',
        26:'z', 27:'', 28:'k', 29:'M', 30:'B', 31:'T'})

    if option.find('%')+1:
        sci_number *= 100

    if sci_number>0:
        # Extract exponent value.
        exponent_value = np.floor(np.log10(np.abs(float(sci_number)))).astype(int)
        exp_decimal_part, exp_whole_part = modf(exponent_value/3)

        # Remove exponent from sci_number and multiply the result by either 1, 10, or 100.
        notation_multiplier = 10**((10*exp_decimal_part-exp_decimal_part)/3)
        new_number = sci_number*notation_multiplier/(10**float(exponent_value))

        # Convert exponent_value to letter format.
        if exp_whole_part <= 4: # sci_number < 10**15
            letters = number_letter_dict[exp_whole_part+27]
        else: # sci_number >= 10**15
            key_decimal_part, key_whole_part = modf((exp_whole_part-5)/26)
            letters = (number_letter_dict[round(key_whole_part+1)]
                + number_letter_dict[round(key_decimal_part*26+1)])

        output = str("%.2f"%new_number)+letters
    else:
        # Avoid errors from taking log(0).
        output = str("%.2f"%sci_number)

    # Display options
    if option.find('%')+1:
        output += '%'
    if option.find(',')+1:
        output += ','
    if option.find('\t')+1:
        output = '\t'+output

    return output

if __name__ == '__main__':
    # Run directly to print out input values.
    GameData('voodoo_playerinput.csv').print_info()