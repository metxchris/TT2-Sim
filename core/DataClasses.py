from __future__ import division, print_function
import numpy as np
from copy import deepcopy
from math import modf
from os import getcwd
from ServerVarsModel import SVM

"""
Notes on Python v2.7 compatibility:
* I've made so many changes since launch that I have no idea how
  much effort would be needed to get this to work in python 2.7 again.

Instructions:
* This file can be directly run to split out tables of all input data
  used in the simulation; just make sure your input file is correctly
  set at the bottom of this code.
"""

def dir_path():
    return '' if getcwd().split('\\')[-1]=='TT2-Sim' else '..\\'
  
class GameData(object):
    def __init__(self, input_file):

        self.input = np.genfromtxt(dir_path()+'player\\'+input_file, delimiter=',', dtype=str)
        self.username = input_file.split('.')[0]
        self.advanced = AdvancedOptions()
        self.artifacts = Artifacts(self.input, self.advanced)
        self.active_skills = ActiveSkills(self.input, self.artifacts, self.advanced)
        self.equipment = Equipment(self.input, self.advanced)
        self.heroes = Heroes(self.input, self.advanced)
        self.hero_multipliers = HeroImprovements(self.heroes.level.size, self.advanced)
        self.hero_skills = HeroSkills(self.heroes.id.size, self.advanced)
        self.pets = Pets(self.input, self.advanced)
        self.skill_tree = SkillTree(self.input, self.advanced)
        self.sword_master = SwordMaster()
        self.stage = Stage(self.advanced.stage_cap, self.skill_tree,
                            self.equipment.titan_hp, self.artifacts)

    def print_info(self, stage_skip_factor=100):
        N = self.advanced.scientific_notation
        print('INPUT VALUES FOR:', self.username)
        self.active_skills.print_info(N)
        self.artifacts.print_info(N)
        self.equipment.print_info(N)
        self.heroes.print_info(N)
        self.pets.print_info(N)
        self.skill_tree.print_info(N)
        self.stage.print_info(stage_skip_factor, N)


class AdvancedOptions(object):
    def __init__(self):
        # Pull advanced options from AdvancedOptions.CSV.
        advanced_csv = np.genfromtxt(dir_path()+'AdvancedOptions.csv', delimiter=',', dtype=str)
        start_idx = np.array([advanced_csv[:,0]=='ADVANCED OPTIONS']).argmax()+1
        end_idx = np.array([advanced_csv[start_idx:,0]=='']).argmax()+1
        advanced_values = advanced_csv[start_idx:end_idx,0].astype(np.float)
        advanced_type = advanced_csv[start_idx:end_idx,1]

        def get_advanced(advanced_name):
            # Avoids crashes if new advanced options are missing.
            if (advanced_type==advanced_name).any():
                value = advanced_values[advanced_type==advanced_name][0]
            else:
                value = 0
                if advanced_name=='HeroLevelCap' or advanced_name=='SwordMasterLevelCap':
                    value = 6000
                print('WARNING: Missing advanced option for:', advanced_name)
                print(' '*8,'Please update AdvancedOptions.csv to the most recent version.\n')
            return value

        # Cap Options.
        self.stage_cap = get_advanced('StageCap')
        self.hero_cap = get_advanced('HeroLevelCap')
        self.sword_master_cap = get_advanced('SwordMasterLevelCap')
        self.levels_to_buy = int(get_advanced('LevelsToBuy'))

        # 1 = Scientific notation, 0 = Letter notation.
        self.scientific_notation = get_advanced('UseScientificNotation')

        # Disable Engine Components.
        self.disable_active_skills = get_advanced('DisableActiveSkills')
        self.disable_artifact_bonuses = get_advanced('DisableArtifactBonuses')
        self.disable_artifact_damage = get_advanced('DisableArtifactDamage')
        self.disable_clan_bonus = get_advanced('DisableClanBonus')
        self.disable_clan_ship = get_advanced('DisableClanShip')
        self.disable_equipment = get_advanced('DisableEquipment')
        self.disable_heroes = get_advanced('DisableHeroes')
        self.disable_hero_improvement = get_advanced('DisableHeroImprovementBonuses')
        self.disable_hero_skills = get_advanced('DisableHeroSkills')
        self.disable_hero_weapons = get_advanced('DisableHeroWeapons')
        self.disable_pet_attack = get_advanced('DisablePetAttack')
        self.disable_pet_bonuses = get_advanced('DisablePetBonuses')
        self.disable_skill_tree = get_advanced('DisableSkillTree')
        self.disable_sword_master = get_advanced('DisableSwordMaster')
    

class ActiveSkills(object):
    def __init__(self, input_csv, artifacts, advanced):
        from numpy.core import defchararray

        csv_data = np.genfromtxt(dir_path()+'data\\ActiveSkillInfo.csv', 
            delimiter=',', dtype=str)
        csv_split = defchararray.rsplit(csv_data, '/')

        # Find active skill info in player input CSV.
        start_idx = np.array([input_csv[:,0]=='ACTIVE SKILL LEVELS']).argmax()+1
        end_idx = start_idx + 6
        skill_levels = input_csv[start_idx:end_idx,0].astype(np.int)
        types = input_csv[start_idx:end_idx, 1]
        active = (input_csv[start_idx:end_idx, 2]!='')

        a = np.array([0])
        hs_level = max(a, skill_levels[(types=='HeavenlyStrike')*active])[0]
        cs_level = max(a, skill_levels[(types=='CriticalStrike')*active])[0]
        hom_level = max(a, skill_levels[(types=='HandOfMidas')*active])[0]
        fs_level = max(a, skill_levels[(types=='FireSword')*active])[0]
        wc_level = max(a, skill_levels[(types=='WarCry')*active])[0]
        sc_level = max(a, skill_levels[(types=='ShadowClone')*active])[0]

        self.levels = np.array([hs_level, cs_level, hom_level, 
            fs_level, wc_level, sc_level])
        self.effects = np.zeros(6)
        self.mana_costs = np.zeros(6)
        self.durations = np.zeros(6)
        self.cooldowns = np.zeros(6)

        for i, level in enumerate(self.levels):
            if level:
                self.effects[i] = (float(csv_split[i+1, 1][level-1]) 
                    * (1 - advanced.disable_active_skills))
                self.durations[i] = (int(csv_split[i+1, 4][0])
                    + artifacts.skill_durations[i])
                self.cooldowns[i] = int(csv_split[i+1, 6][0])
                self.mana_costs[i] = (int(csv_split[i+1, 9][level-1])
                    - artifacts.skill_cost_red[i])

    def print_info(self, N=0):
        names = (['Heavenly Strike', 'Critical Strike', 'Hand of Midas',
            'Fire Sword', 'War Cry', 'Shadow Clone'])
        print('')
        print('ACTIVE SKILL NAME'.ljust(22), '\t'+'LEVEL'.rjust(5),
            '\t'+'BASE EFFECT'.rjust(12), '\t'+'MANA COST'.rjust(9),
            '\t'+'DURATION'.rjust(8), '\t'+'COOLDOWN'.rjust(8))
        for i, name in enumerate(names):
            if (self.levels[i]==0):
                continue
            print(name.ljust(22), '\t'+str(self.levels[i]).rjust(5), 
                '\t'+str('%.2f'%self.effects[i]).rjust(12), 
                '\t'+str(self.mana_costs[i]).rjust(9),
                '\t'+str(self.durations[i]).rjust(8),
                '\t'+str(self.cooldowns[i]).rjust(8))


class Artifacts(object):
    def __init__(self, input_csv, advanced):
        artifacts_csv = np.genfromtxt(dir_path()+'data\\ArtifactInfo.csv', 
            delimiter=',', dtype=str)

        # Find artifact info in player input CSV.
        start_idx = np.array([input_csv[:,0]=='ARTIFACT LEVELS']).argmax()+1
        end_idx = start_idx + artifacts_csv[1:,0].size

        # Advanced Options
        disable_bonuses = advanced.disable_artifact_bonuses
        disable_damage = advanced.disable_artifact_damage

        self.id = artifacts_csv[1:,0]
        self.name = artifacts_csv[1:,9]
        self.max_level = artifacts_csv[1:,1].astype(np.int)
        self.type = artifacts_csv[1:,3]
        self.effect_inc = artifacts_csv[1:,4].astype(np.float)
        self.damage_inc = artifacts_csv[1:,5].astype(np.float)
        self.cost_coef = artifacts_csv[1:,6].astype(np.float)
        self.cost_expo = artifacts_csv[1:,7].astype(np.float)

        # Set artifact effects and damages based on player artifact levels.
        self.level = input_csv[start_idx:end_idx, 0].astype(np.int)
        self.effect = self.effect_inc*self.level * (1 - disable_bonuses)
        self.damage = self.damage_inc*self.level * (1 - disable_damage)

        # Add base level to effect multipliers where needed.
        artifact_names = ('Furies Bow', 'Heavenly Sword', 'Fruit of Eden', 
            'Charm of the Ancient', 'The Sword of Storms', 'Book of Prophecy',
            'Drunken Hammer', 'Divine Retribution', 'Laborer\'s Pendant',
            'Blade of Damocles', 'Parchment of Foresight', 'Heroic Shield',
            'Stone of the Valrunes', 'Elixir of Eden', 'Bringer of Ragnarok',
            'Titan\'s Mask', 'Chest of Contentment', 'Hero\'s Blade',
            'Helmet of Madness', 'Lethe Water', 'Amethyst Staff',
            'Book of Shadows')
        for name in artifact_names:
            self.effect[self.name==name] += 1

        # Total artifact damage bonus.
        self.total_damage = max(1, (1+np.sum(self.damage))
            * self.effect[self.name=='Heavenly Sword'][0]
            * (1 - disable_damage))
        # Active skill bonuses.
        self.hs_bonus = self.effect[self.name=='Titan\'s Mask'][0]
        self.hom_bonus = self.effect[self.name=='Laborer\'s Pendant'][0]
        self.wc_bonus = self.effect[self.name=='Parchment of Foresight'][0]
        self.sc_bonus = self.effect[self.name=='Elixir of Eden'][0]
        self.fs_bonus = self.effect[self.name=='Bringer of Ragnarok'][0]
        # Damage type bonuses.
        self.all_damage = self.effect[self.name=='Divine Retribution'][0]
        self.all_hero_damage = self.effect[self.name=='Blade of Damocles'][0]
        self.melee_damage = self.effect[self.name=='Fruit of Eden'][0]
        self.spell_damage = self.effect[self.name=='Charm of the Ancient'][0]
        self.ranged_damage = self.effect[self.name=='The Sword of Storms'][0]
        self.pet_damage = self.effect[self.name=='Furies Bow'][0]
        self.tap_damage = self.effect[self.name=='Drunken Hammer'][0]
        self.crit_chance = self.effect[self.name=='Axe of Muerte'][0]
        # Gold bonuses.
        self.all_gold = self.effect[self.name=='Book of Prophecy'][0]
        self.titan_gold = self.effect[self.name=='Stone of the Valrunes'][0]
        self.boss_gold = self.effect[self.name=='Heroic Shield'][0]
        self.chest_gold = self.effect[self.name=='Chest of Contentment'][0]
        self.chest_chance = self.effect[self.name=='Egg of Fortune'][0]
        self.x10_gold_chance = self.effect[self.name=='Divine Chalice'][0]
        self.cost_reduction = self.effect[self.name=='Staff of Radiance'][0]
        # Active Skill Related.
        duration_artifacts = (['Forbidden Scroll', 'Ring of Fealty', 
            'Glacial Axe', 'Aegis', 'Swamp Gauntlet'])
        cost_red_artifacts = (['Infinity Pendulum', 'Glove of Kuma', 'Titan Spear',
            'Oak Staff', 'The Arcana Cloak', 'Hunter\'s Ointment'])
        self.skill_durations = np.zeros(6)
        self.skill_cost_red = np.zeros(6)
        for i, artifact in enumerate(duration_artifacts):
            self.skill_durations[i+1] = self.effect[self.name==artifact][0]
        for i, artifact in enumerate(cost_red_artifacts):
            self.skill_cost_red[i] = self.effect[self.name==artifact][0]

    def print_info(self, N=0):
        print('')
        print('ARTIFACT NAME'.ljust(22),
            '\t'+'LEVEL'.rjust(5),
            '\t'+'EFFECT'.rjust(6),
            '\t'+'DAMAGE'.rjust(8))
        for i, name in enumerate(self.name):
            if (self.level[i]==0):
                continue
            print(name.ljust(22), 
                '\t'+str(self.level[i]).rjust(5), 
                '\t'+str('%.2f'%self.effect[i]).rjust(6), 
                '\t'+notate(self.damage[i], N, '%').rjust(8))
        print('Total Artifact Damage:', notate(self.total_damage, N, '%'))


class Equipment(object):
    def __init__(self, input_csv, advanced):
        """
        I won't be using EquipmentInfo.csv to generate equipment values until
        the in-game displayed equipment levels are fixed.  At this point, using
        real levels isn't any more accurate than having the player enter
        their rounded equipment multipliers directly.
        """

        #equip_csv = np.genfromtxt('..\\data\\EquipmentInfo.csv', delimiter=',', dtype=str)

        # Equipment formula:
        #double num3 = num * (this.attributeBase + this.attributeInc * (double)num2);
        #num2 = this.level
        #num = artifact bonus
        #Mathf.Max(1, Mathf.FloorToInt((float)(this.currentEquipment.level / 10)
        # Your real equipment level is Level*10 + 4.5, on average.
        # Store-bought items might always be Level*10 + 9 (this is true for max items)

        start_idx = np.array([input_csv[:,0]=='EQUIPMENT MULTIPLIERS']).argmax()+1
        end_idx = start_idx + np.array([input_csv[start_idx:,0]=='']).argmax()
        types = input_csv[start_idx:end_idx, 1]
        effects = input_csv[start_idx:end_idx, 0].astype(np.float)
        equipped = (input_csv[start_idx:end_idx, 2]!='')

        if advanced.disable_equipment:
            equipped[:] = False

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
        self.pet_damage = max(b, effects[(types=='PetDamage')*equipped])[0]
        self.crit_damage = max(b, effects[(types=='CritDamage')*equipped])[0]
        self.crit_chance = max(a, effects[(types=='CritChance')*equipped])[0]
        self.titan_hp = min(b, effects[(types=='TitanHP')*equipped])[0]
        self.tap_damage = max(b, effects[(types=='TapDamage')*equipped])[0]

    def print_info(self, N=0):
        names = ('Sword',)*3+('Helmet',)*3+('Armor',)*2+('Aura',)*3+('Slash',)*2
        types = ('AllDamage', 'AllHeroDamage', 'CritDamage', 'MeleeDamage',
            'SpellDamage', 'RangedDamage', 'AllGold', 'ChestGold', 'CritChance',
            'ChestChance', 'TitanHP', 'PetDamage', 'TapDamage')
        effects = (self.all_damage, self.all_hero_damage, self.crit_damage, 
            self.melee_mult, self.spell_mult, self.ranged_mult,
            self.all_gold, self.chest_gold, self.crit_chance, self.chest_chance,
            self.titan_hp, self.pet_damage, self.tap_damage)

        print('')
        print('EQUIPMENT'.ljust(10), '\t'+'TYPE'.ljust(13), '\t'+'EFFECT'.rjust(6))
        for i, j in enumerate(types):
            if (effects[i]==1 or effects[i]==0):
                continue
            print(names[i].ljust(10), '\t'+types[i].ljust(13),
                '\t'+str(effects[i]).rjust(6))


class Heroes(object):
    def __init__(self, input_csv, advanced):
        # Read CSV Files.
        helper_info = np.genfromtxt(dir_path()+'data\\HelperInfo.csv', 
            delimiter=',', dtype=str)
        helper_names = np.genfromtxt(dir_path()+'data\\HelperNames.csv', 
            delimiter=',', dtype=str)
        id_size = helper_info[1:,0].size

        # Weapon level location in player input CSV.
        start_idx = np.array([input_csv[:,0]=='HERO WEAPON LEVELS']).argmax()+1
        end_idx = start_idx + id_size

        disable_weapons = advanced.disable_hero_weapons

        # Initialize Hero Information.
        self.id = helper_info[1:,0]
        self.name = helper_names[1:,1]
        self.unlock_order = helper_info[1:,1].astype(np.int)
        self.type = helper_info[1:,2]
        self.purchase_cost = helper_info[1:,3].astype(np.float)
        self.level = np.zeros(id_size, dtype=np.int)
        self.weapon_levels = (input_csv[start_idx:end_idx, 0].astype(np.int)
            * (1 - disable_weapons))
        self.weapon_bonus = (1 + self.weapon_levels/2)
        self.set_bonus = max(1, 
            10 * (self.weapon_levels.min()) * (1 - disable_weapons))

        self.melee_type = self.type=='Melee'
        self.spell_type = self.type=='Spell'
        self.ranged_type = self.type=='Ranged'

    def print_info(self, N=0):
        print('')
        print('HEROES: NAME'.ljust(30), '\t'+'TYPE'.ljust(10),
            '\t'+'BASE COST'.rjust(9), '\t'+'W. LEVEL'.rjust(10),
            '\t'+'W. BONUS'.rjust(10))
        for i, name in enumerate(self.name):
            print(name.ljust(30), '\t'+self.type[i].ljust(10), 
                '\t'+notate(self.purchase_cost[i], N).rjust(9),
                '\t'+str(self.weapon_levels[i]).rjust(10),
                '\t'+str(self.weapon_bonus[i]).rjust(10))
        print('Set Bonus:', 'x'+notate(self.set_bonus, N))


class HeroImprovements(object):
    def __init__(self, level_size, advanced):
        improvements_info = np.genfromtxt(dir_path()+'data\\HelperImprovementsInfo.csv', 
            delimiter=',', dtype=str)   
        
        self.levels = np.zeros(improvements_info[1:,0].size+2, dtype=np.int)
        self.levels[1] = 1
        self.levels[2:] = improvements_info[1:,0].astype(np.int)
        self.bonuses = np.zeros(improvements_info[1:,2].size+2)
        self.bonuses[1] = 1
        self.bonuses[2:] = improvements_info[1:,2].astype(np.float)
        if advanced.disable_hero_improvement:
            self.bonuses[2:] = 1
        self.level_tile = np.tile(self.levels, (level_size, 1))
        self.bonus_tile = np.tile(self.bonuses, (level_size, 1))


class HeroSkills(object):
    def __init__(self, id_size, advanced):
        csv_data = np.genfromtxt(dir_path()+'data\\HelperSkillInfo.csv', 
            delimiter=',', dtype=str)
        self.bonus_id_tile = np.tile(csv_data[1:, 1], (id_size, 1))
        self.bonus_type_tile = np.tile(csv_data[1:, 3], (id_size, 1))
        self.bonus_mult_tile = np.tile(csv_data[1:, 4].astype(np.float), (id_size, 1)) 
        self.bonus_level_tile = np.tile(csv_data[1:, 5].astype(np.int), (id_size, 1))
        if advanced.disable_hero_skills:
            self.bonus_level_tile[:] = 10**6



class Pets(object):
    def __init__(self, input_csv, advanced):
        # Game data.
        pet_csv = np.genfromtxt(dir_path()+'data\\PetInfo.csv', delimiter=',', dtype=str)
        dmg_base = pet_csv[1:,1].astype(np.float)
        dmg_inc = pet_csv[1:,2:5].astype(np.float)
        bonus_base = pet_csv[1:,6].astype(np.float)
        bonus_inc = pet_csv[1:,7].astype(np.float)

        # Find pet info locations in player input CSV.
        start_idx = (input_csv[:,0]=='PET LEVELS').argmax()+1
        end_idx = start_idx + pet_csv[1:,1].size
        active_idx = (input_csv[start_idx:end_idx,2]!='').argmax()

        disable_bonuses = advanced.disable_pet_bonuses

        # Initialize object values.
        self.id = pet_csv[1:,0]
        self.bonus_type = pet_csv[1:,5]
        self.level = input_csv[start_idx:end_idx, 0].astype(np.int)
        self.name = input_csv[start_idx:end_idx, 1]
        self.active_name = input_csv[start_idx:end_idx, 1][active_idx]

        # Compute arrays of active values for each pet.
        self.active_damage = (dmg_base + np.minimum(self.level, 40)*dmg_inc[:,0]
            + np.maximum(np.minimum(self.level-40, 40), 0)*dmg_inc[:,1]
            + np.maximum(self.level-80, 0)*dmg_inc[:,2]) * (1 - disable_bonuses)
        self.active_bonus = ((bonus_base + self.level*bonus_inc)
            * (1 - disable_bonuses))

        # Compute arrays of passive values for each pet.
        self.passive_factor = np.minimum(0.05*np.floor(self.level/5), 1)
        self.passive_bonus = (self.active_bonus-bonus_base)*self.passive_factor
        self.passive_bonus[self.passive_factor>0] += bonus_base[self.passive_factor>0]
        self.passive_bonus *= (1 - disable_bonuses)
        self.passive_damage = self.active_damage*self.passive_factor * (1 - disable_bonuses)

        # Compute total bonus multipliers based on active pet.
        active_idx = (self.name==self.active_name)
        self.bonus_multipliers = deepcopy(self.passive_bonus)
        self.bonus_multipliers[active_idx] = self.active_bonus[active_idx]
        #self.bonus_multipliers[:-1][self.bonus_multipliers[:-1]==0] = 1

        # Compute total damage bonus based on active pet.
        self.damage_mult = (self.active_damage[self.name==self.active_name][0]
            + self.passive_damage[self.name!=self.active_name].sum() + 1)

        # Type bonuses.
        pet_bt = self.bonus_type
        pet_bv = self.bonus_multipliers

        self.all_damage = max(1, pet_bv[pet_bt=='AllDamage'].prod())
        self.all_hero_damage = max(1, pet_bv[pet_bt=='AllHelperDamage'].prod())
        self.melee_damage = max(1, pet_bv[pet_bt=='MeleeHelperDamage'].prod())
        self.spell_damage = max(1, pet_bv[pet_bt=='SpellHelperDamage'].prod())
        self.ranged_damage = max(1, pet_bv[pet_bt=='RangedHelperDamage'].prod())
        self.tap_damage = max(1, pet_bv[pet_bt=='TapDamage'].prod())
        self.all_gold = max(1, pet_bv[pet_bt=='GoldAll'].prod())
        self.splash_damage = pet_bv[pet_bt=='SplashDamage'][0]
        self.mana_regen = pet_bv[pet_bt=='ManaRegen'][0]

    def print_info(self, N=0):
        print('')
        print('PET NAME'.ljust(8), '\t'+'LEVEL'.rjust(5),
            '\t'+'P. BONUS'.rjust(8), '\t'+'P. DAMAGE'.rjust(9),
            '\t'+'A. BONUS'.rjust(8), '\t'+'A. DAMAGE'.rjust(9))
        for i, name in enumerate(self.name):
            print(name.ljust(8), '\t'+str(self.level[i]).rjust(5), 
                '\t'+str("%.3f"%self.passive_bonus[i]).rjust(8), 
                '\t'+notate(self.passive_damage[i], N, "%").rjust(9),  
                '\t'+str("%.2f"%self.active_bonus[i]).rjust(8),  
                '\t'+notate(self.active_damage[i], N, "%").rjust(9),
                '\tActive' if name==self.active_name else '')
        c1, c2 = 15, 5
        print('\nTOTAL PET BONUSES:',
            '\nAllDamage'.ljust(c1), str('%.2f'%self.all_damage).rjust(c2),
            '\nAllHeroDamage'.ljust(c1), str('%.2f'%self.all_hero_damage).rjust(c2),
            '\nMeleeDamage'.ljust(c1), str('%.2f'%self.melee_damage).rjust(c2),
            '\nSpellDamage'.ljust(c1), str('%.2f'%self.spell_damage).rjust(c2),
            '\nRangedDamage'.ljust(c1), str('%.2f'%self.ranged_damage).rjust(c2),
            '\nTapDamage'.ljust(c1), str('%.2f'%self.tap_damage).rjust(c2),
            '\nAllGold'.ljust(c1), str('%.2f'%self.all_gold).rjust(c2),
            '\nSplash'.ljust(c1), str('%.2f'%self.splash_damage).rjust(c2),
            '\nManaRegen'.ljust(c1), str('%.2f'%self.mana_regen).rjust(c2))


class SkillTree(object):
    def __init__(self, input_csv, advanced):
        skill_tree_csv = np.genfromtxt(dir_path()+'data\\SkillTreeInfo.csv',
            delimiter=',', dtype=str)
        skill_tree_csv[skill_tree_csv == '-'] = 'NaN' # needed for setting float type here.

        # Find skill tree info locations in player input CSV.
        start_idx = np.array([input_csv[:, 0]=='SKILL TREE LEVELS']).argmax()+1
        end_idx = start_idx + skill_tree_csv[1:, 0].size

        self.attributes = skill_tree_csv[1:, 0]
        self.effect_level = skill_tree_csv[1:, 25:].astype(np.float)
        self.name = input_csv[start_idx:end_idx, 1]
        self.level = input_csv[start_idx:end_idx, 0].astype(np.int)
        if advanced.disable_skill_tree:
            self.level[:] = 0
        self.effect = np.zeros(self.level.size)

        for i, j in enumerate(self.level):
            self.effect[i] = self.effect_level[i, self.level[i]]

        def get_skill(skill_name):
            if (self.attributes==skill_name).any():
                effect = self.effect[self.attributes==skill_name][0]
            else:
                print('ERROR: Could not find', skill_name, 'skill in input file.')
                effect = 0
            return effect

        # Active Skill Bonuses.
        self.wc_bonus = get_skill('HelperDmgSkillBoost')
        self.hs_bonus = get_skill('BurstSkillBoost')
        self.fs_bonus = get_skill('FireTapSkillBoost')
        # Damage Bonuses.
        self.pet_damage = max(get_skill('PetDmg'), 1)
        self.melee_damage = max(get_skill('MeleeHelperDmg'), 1)
        self.spell_damage = max(get_skill('SpellHelperDmg'), 1)
        self.ranged_damage = max(get_skill('RangedHelperDmg'), 1)
        self.splash_damage = get_skill('SplashDmg')
        # Mana Related.
        self.mana_siphon = get_skill('ManaStealSkillBoost')
        self.mana_regen = get_skill('MPRegenBoost')
        self.mana_capacity = get_skill('MPCapacityBoost')
        self.manni_mana = get_skill('ManaMonster')
        # Misc Effects.
        self.flash_zip = get_skill('BossDmgQTE')
        self.boss_timer = get_skill('BossTimer')
        self.tf_chance = get_skill('MultiMonsters')

    def print_info(self, N=0):
        print('')
        print('SKILL TREE: NAME'.ljust(25), '\t'+'LEVEL'.rjust(5), '\t'+'EFFECT'.rjust(6))
        for i, j in enumerate(self.level):
            if (self.level[i]==0):
                continue
            print(self.name[i].ljust(25), 
                '\t'+str(self.level[i]).rjust(5), 
                ' \t'+str(self.effect[i]).rjust(6))
        

class SwordMaster(object):
    def __init__(self):
        improvements_info = np.genfromtxt(dir_path()+'data\\PlayerImprovementsInfo.csv', 
            delimiter=',', dtype=str)   
        
        self.levels = improvements_info[1:,0].astype(np.int)
        level_bonuses = improvements_info[1:,1].astype(np.float)
        self.multipliers = np.zeros_like(level_bonuses)
        for i, m in enumerate(level_bonuses):
            self.multipliers[i] = level_bonuses[:i+1].prod()


class Stage(object):
    def __init__(self, stage_cap, skill_tree, hp_multiplier, artifacts):
        # Simulation prone to crash above stage 5250.
        self.cap = min(stage_cap, 5250)
        self.number = np.arange(self.cap + 1).astype(np.int)

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

        ip_level = skill_tree.effect[skill_tree.attributes=='LessMonsters'][0].astype(np.int)
        self.titan_count = np.maximum(1, 
            (10 + np.minimum(np.floor(self.number/1000)*4, 20))-ip_level).astype(np.int)

        # The player.all_gold multiplier is supposed to be here, but we will
        # apply it as monsters are killed.
        self.base_titan_gold = (self.titan_hp*SVM.monsterGoldMultiplier
            + SVM.monsterGoldSlope*np.minimum(self.number, SVM.noMoreMonsterGoldSlope))
        self.base_titan_gold[0] = 30 # Ensures enough starting gold to purchase first hero.
        self.base_boss_gold = (self.boss_hp*SVM.monsterGoldMultiplier
            + SVM.monsterGoldSlope*np.minimum(self.number, SVM.noMoreMonsterGoldSlope))
        self.base_boss_gold[0] = 30 # Ensures enough starting gold to purchase first hero.

        BOS_mult = artifacts.effect[artifacts.name=='Book of Shadows']
        self.relics = (BOS_mult*((np.maximum(0, self.number - 75)
            / 14)**1.75)).astype(np.int)

        self.transitions = np.zeros_like(self.number)
        self.transitions[0::5] =  1

    def print_info(self, stage_skip_factor, N=0):
        # Print to screen all values of every stage_skip_factor stages.
        print('')
        print('STAGE'.rjust(5),
            '\t'+'TITAN HP'.rjust(10),
            '\t'+'BOSS HP'.rjust(10),
            '\t'+'BASE GOLD'.rjust(10),
            '\t'+'TITAN #'.rjust(7),
            '\t'+'RELICS'.rjust(7))
        for i in range(1, int(self.cap/stage_skip_factor)+1):
            print(str(i*stage_skip_factor).rjust(5),
                '\t'+notate(self.titan_hp[i*stage_skip_factor], N).rjust(10),
                '\t'+notate(self.boss_hp[i*stage_skip_factor], N).rjust(10),
                '\t'+notate(self.base_titan_gold[i*stage_skip_factor], N).rjust(10),
                '\t'+str(self.titan_count[i*stage_skip_factor]).rjust(7),
                '\t'+str(self.relics[i*stage_skip_factor]).rjust(7)) 


def notate(sci_number, use_sci=0, option=''):
    """
    Input: Any number, ideally one that requires scientific notation to display.
    Returns: String in the form of ###.##aa, where aa is the associated letter pair.
    """

    if option.find('%')+1:
        sci_number *= 100

    number_letter_dict = ({1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g',
        8:'h', 9:'i', 10:'j', 11:'k', 12:'l', 13:'m', 14:'n', 15:'o', 16:'p',
        17:'q', 18:'r', 19:'s', 20:'t', 21:'u', 22:'v', 23:'w', 24:'x', 25:'y',
        26:'z', 27:'', 28:'k', 29:'M', 30:'B', 31:'T'})

    if sci_number>1:
        # Extract exponent value.
        exponent_value = np.floor(np.log10(np.abs(float(sci_number)))).astype(int)
        exp_decimal_part, exp_whole_part = modf(exponent_value/3)

        # Remove exponent from sci_number and multiply the result by either 1, 10, or 100.
        notation_multiplier = 10**((10*exp_decimal_part-exp_decimal_part)/3)
        new_number = sci_number*notation_multiplier/(10**float(exponent_value))

        # Convert exponent_value to letter format.
        if exp_whole_part <= 4: # sci_number < 10**15
            notate = number_letter_dict[exp_whole_part+27]
        else: # sci_number >= 10**15
            key_decimal_part, key_whole_part = modf((exp_whole_part-5)/26)
            notate = (number_letter_dict[round(key_whole_part+1)]
                + number_letter_dict[round(key_decimal_part*26+1)])

        if use_sci and exp_whole_part>4:
            output = str("%.2e"%sci_number).replace('+', '')
        else:
            output = str("%.2f"%new_number)+notate

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

def convert_time(time_in_seconds):
    """ converts a number in seconds to an appropriate unit of time. """

    minute = 60
    hour = 60*minute
    day = 24*hour
    year = 365*day
    century = 100*year

    if time_in_seconds < minute: 
        output_time = str('%.2f'%time_in_seconds)+' sec '
    elif time_in_seconds < hour: 
        output_time = str('%.2f'%(time_in_seconds/minute))+' mins'
    elif time_in_seconds < day: 
        output_time = str('%.2f'%(time_in_seconds/hour))+' hrs '
    elif time_in_seconds < year: 
        output_time = str('%.2f'%(time_in_seconds/day))+' days'
    elif time_in_seconds < century: 
        output_time = str('%.2f'%(time_in_seconds/year))+' yrs '
    else:
        output_time = notate(time_in_seconds/century, 1)+' yrs '
    return output_time

if __name__ == '__main__':
    # Run directly to print out input values.
    GameData('SwordMaster.csv').print_info()