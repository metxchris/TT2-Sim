from __future__ import division, print_function
import numpy as np
from math import modf
from time import time
from copy import deepcopy
from Classes import GameData, letters
from Plotting import plot_results, plot_splash
from ServerVarsModel import SVM

"""
TODO:
1. Add Sword Master damage.
2. Add Equipment CSV, test if works (it doesn't).
3. Sci format option.
4. SwordMaster upgrades + FS + SC
"""

class Player(object):
    def __init__(self, data, advanced_results):

        # Unpack data object.
        input_csv = data.input
        pets = data.pets
        artifacts = data.artifacts
        equipment = data.equipment
        skill_tree = data.skill_tree
        heroes = data.heroes
        hero_skills = data.hero_skills
        active_skills = data.active_skills
        stage = data.stage

        # Pull general input values from PlayerInput.CSV.
        start_idx = np.array([input_csv[:,0]=='GENERAL INPUT VALUES']).argmax()+1
        end_idx = np.array([input_csv[start_idx:,0]=='']).argmax()+1
        input_values = input_csv[start_idx:end_idx,0].astype(np.int)
        input_type = input_csv[start_idx:end_idx,1]
        
        # Advanced results will print more details but increases run time.
        self.advanced_results = advanced_results
        if self.advanced_results:
            self.evolve1_stage = np.zeros_like(heroes.level)
            self.evolve2_stage = np.zeros_like(heroes.level)
            self.max_splash_stages = np.zeros(4, dtype=np.int)
            self.continuous_splash_stages = np.zeros_like(self.max_splash_stages)
            self.splash_array = np.zeros_like(stage.number, dtype=np.int)
            self.splash_array_penalty = np.zeros_like(self.splash_array)

        # Store player input values.
        self.clan_level = max(input_values[input_type=='ClanLevel'][0], 1)
        self.start_stage = max(input_values[input_type=='StartStage'][0], 1)
        self.stage_cap = input_values[input_type=='StageCap'][0]
        self.hero_cap = input_values[input_type=='HeroLevelCap'][0]
        self.taps_sec = min(input_values[input_type=='TapsPerSec'][0], 20)
        self.clan_size = min(input_values[input_type=='ClanSize'][0], 50)

        # Initialize Default Values.
        self.hero_level = heroes.level
        self.hero_dps = np.zeros_like(self.hero_level, dtype=np.float)
        self.default_levels_to_buy = 10*np.ones_like(heroes.level).astype(np.int)
        self.hero_multiplier = np.zeros_like(heroes.level, dtype=np.float)
        self.stage_duration_stages = np.zeros(3, dtype=np.int)
        self.heroes_bought = False
        self.end_simulation = False
        self.time = 0

        # Initialize variables to be updated later.
        self.sword_master_damage =0
        self.sword_master_level = 0
        self.pet_damage_per_attack = 0
        self.tap_damage_from_hero = 0
        self.tap_with_average_crit = 0
        self.crit_damage = 0
        self.crit_chance = 0
        self.boss_gold = 0
        self.chest_gold = 0
        self.chest_chance = 0
        self.titan_gold = 0
        self.all_gold = 0
        self.all_damage = 0
        self.all_hero_damage = 0
        self.melee_mult = 0
        self.spell_mult = 0
        self.ranged_mult = 0
        self.tap_mult = 0
        self.tap_damage = 0
        self.ship_damage = 0
        self.melee_dps = 0
        self.spell_dps = 0
        self.ranged_dps = 0
        self.pet_dps = 0
        self.total_dps = 0
        self.total_boss_dps = 0

        self.gold_spent = 0

        # Values stored for each stage.
        self.pet_attack_damage_array = np.zeros_like(stage.number, dtype=np.float)
        self.total_dps_array = np.zeros_like(stage.number, dtype=np.float)
        self.gold_array = np.zeros((stage.number.size, 3), dtype=np.float)

        # Clan Quest Bonus.
        self.clan_bonus = (SVM.clanBonusBase**min(self.clan_level, SVM.clanQuestStageNerf)
            * SVM.clanBonusBaseNerf**max(self.clan_level - SVM.clanQuestStageNerf, 0))

        # Initialize active skill bonuses (crit strike activated later).
        self.hom = (active_skills.hom
            * artifacts.effect[artifacts.name=='Laborer\'s Pendant'][0])
        self.war_cry = max(1, active_skills.war_cry
            * artifacts.effect[artifacts.name=='Parchment of Foresight'][0])

        # Pet damage multiplier.
        self.pet_mult = (pets.damage_mult
            * artifacts.effect[artifacts.name=='Furies Bow'][0]
            * skill_tree.effect[skill_tree.attributes=='PetDmg'][0]
            * equipment.pet_mult)

        # Pet auto-attack and attack-rate.
        self.pet_auto = 1 if (pets.level.sum()>=SVM.petAutoAttackLevel) else 0
        self.pet_rate = (self.taps_sec/SVM.tapsPerSecond
            + self.pet_auto/SVM.petAutoAttackDuration)

        # Skill tree values.
        self.flash_zip = skill_tree.effect[skill_tree.attributes=='BossDmgQTE'][0]
        self.boss_timer = 30 + skill_tree.effect[skill_tree.attributes=='BossTimer'][0]

        # Artifact damage multiplier.
        self.artifact_damage = artifacts.total_damage

        # Pet bonus abbreviations used in multipliers below.
        pet_bt = pets.bonus_type
        pet_bv = pets.bonus_multipliers

        # Damage type multipliers
        self.base_all_damage = (pet_bv[pet_bt=='AllDamage'].prod()
            * artifacts.effect[artifacts.name=='Divine Retribution'][0]
            * equipment.all_damage*self.clan_bonus*self.artifact_damage
            * max(1, heroes.set_bonus))
        self.base_all_hero_damage = (pet_bv[pet_bt=='AllHelperDamage'].prod()
            * artifacts.effect[artifacts.name=='Blade of Damocles'][0]
            * equipment.all_hero_damage*self.war_cry)
        self.base_melee_mult = (pet_bv[pet_bt=='MeleeHelperDamage'].prod()
            * artifacts.effect[artifacts.name=='Fruit of Eden'][0]
            * max(1, skill_tree.effect[skill_tree.attributes=='MeleeHelperDmg'][0])
            * equipment.melee_mult)
        self.base_spell_mult = (pet_bv[pet_bt=='SpellHelperDamage'].prod()
            * artifacts.effect[artifacts.name=='Charm of the Ancient'][0]
            * max(1, skill_tree.effect[skill_tree.attributes=='SpellHelperDmg'][0])
            * equipment.spell_mult)
        self.base_ranged_mult = (pet_bv[pet_bt=='RangedHelperDamage'].prod()
            * artifacts.effect[artifacts.name=='The Sword of Storms'][0]
            * max(1, skill_tree.effect[skill_tree.attributes=='RangedHelperDmg'][0])
            * equipment.ranged_mult)
        self.base_tap_mult = (pet_bv[pet_bt=='TapDamage'].prod() #not used
            * artifacts.effect[artifacts.name=='Drunken Hammer'][0]
            * equipment.tap_damage) 
        self.splash_damage = (pet_bv[pet_bt=='SplashDamage'][0]
            + skill_tree.effect[skill_tree.attributes=='SplashDmg'][0])

        # Gold multipliers.
        self.base_all_gold = (pet_bv[pet_bt=='GoldAll'].prod()
            * artifacts.effect[artifacts.name=='Book of Prophecy'][0]
            * equipment.all_gold)
        self.base_titan_gold = artifacts.effect[artifacts.name=='Stone of the Valrunes'][0]
        self.base_boss_gold = artifacts.effect[artifacts.name=='Heroic Shield'][0]
        self.base_chest_gold = (artifacts.effect[artifacts.name=='Chest of Contentment'][0]
            * equipment.chest_gold)
        self.base_chest_chance = (SVM.chestersonChance 
            + artifacts.effect[artifacts.name=='Egg of Fortune'][0]
            + equipment.chest_chance/100)
        self.base_x10_gold_chance = (SVM.goldx10Chance
         + artifacts.effect[artifacts.name=='Divine Chalice'][0])

        # Misc bonuses.
        self.mana_regen = pet_bv[pet_bt=='ManaRegen'][0] #not used yet
        self.base_crit_chance = (SVM.playerCritChance
            + artifacts.effect[artifacts.name=='Axe of Muerte'][0]
            + equipment.crit_chance/100 + active_skills.crit_strike/100)
        self.cost_reduction = artifacts.effect[artifacts.name=='Staff of Radiance'][0]

        # Starting gold (gives boss gold of all stages skipped with min = 30 gold)
        self.stage = self.start_stage
        self.gold_array[0:self.stage, 0] = (3*stage.base_boss_gold[:self.stage]
            *self.base_boss_gold*self.base_all_gold)
        self.current_gold = self.gold_array.sum()

    def buy_heroes(self, heroes):
        """
        Notes:
        1. Gold is only spent on hero purchases and on level upgrades for
        the strongest hero only (highest unlock number).  This is to avoid
        having to write an AI that correctly balances buying hero levels for
        DPS and for improvement bonuses.  Also, hero level costs for heroes
        that are not the main damage source are generally neglible compared
        to level costs of the primary damage hero.
        """

        # Abbreviate self.hero_level to use below.
        level = self.hero_level

        # Reset hero level purchase tracking.
        self.heroes_bought = False

        # Attempt to unlock heroes until all heroes are purchased.
        if (level.min()==0):
            gold_check = self.current_gold>(1-self.cost_reduction)*heroes.purchase_cost

            if (gold_check*(level==0)).any():
                purchase_cost = ((1-self.cost_reduction)
                    * heroes.purchase_cost)[gold_check*(level==0)].max()
                self.gold_spent += purchase_cost
                self.current_gold -= purchase_cost
                level[gold_check*(level==0)] = 1
                self.heroes_bought = True

        # Attempt to buy additional hero levels until no levels are bought.
        keep_buying = True
        while keep_buying:

            # Determine levels_to_buy based on current hero level.
            levels_to_buy = deepcopy(self.default_levels_to_buy)
            levels_to_buy[(level>=self.hero_cap)+(level==0)] = 0
            levels_to_buy[(level==999)+(level==1999)] = 1
            levels_to_buy[(level==1)+(level==990)+(level==1990)] = 9

            # Level costs (this is supposed to be a ceiling, but it isn't needed).
            level_cost = (heroes.purchase_cost*SVM.helperUpgradeBase**level
                * (SVM.helperUpgradeBase**levels_to_buy-1)/(SVM.helperUpgradeBase - 1)
                * (1-self.cost_reduction))
            level_cost[levels_to_buy==1] *= SVM.evolveCostMultiplier

            if self.advanced_results:
                # Store evolve levels for each hero.
                evolve1_level_check = (self.evolve1_stage==0)*(level==1000)
                evolve2_level_check = (self.evolve2_stage==0)*(level==2000)
                self.evolve1_stage[evolve1_level_check] = self.stage
                self.evolve2_stage[evolve2_level_check] = self.stage

            # Apply level gain.  (level_cost==0 implies levels_to_buy==0.)
            gold_check = self.current_gold>level_cost
            self.hero_level[gold_check] += levels_to_buy[gold_check]
            
            # Check if hero levels were bought.
            keep_buying = (gold_check*(levels_to_buy>0)).any()

            # Flag if hero levels were bought.
            if keep_buying:
                self.heroes_bought = True

                # Spend gold on strongest hero level cost only.
                strongest_hero_cost = level_cost[level>0][-1]
                if (self.current_gold>=strongest_hero_cost):
                    self.gold_spent += strongest_hero_cost
                    self.current_gold -= strongest_hero_cost

    def hero_improvement_bonuses(self, data):
        """ 
        This is what the hero damage multiplier code is doing:
            for i, hero_id in enumerate(heroes.id):
                condition = (self.hero_level[i]>=multipliers.levels)
                self.hero_multiplier[i] = multipliers.bonuses[condition].max()

        The hero skill multiplier section is similar, but more involved.

        Known Accuracy Issues:
        1. There is no gold-check for hero skill multipliers.  Skill upgrade
        costs aren't that expensive and getting a skill like 1.1x all damage
        a stage early won't make much of a difference.
        """

        if self.heroes_bought:

            heroes = data.heroes
            skills = data.hero_skills
            multipliers = data.hero_multipliers
        
            # Hero damage multipliers (improvement bonus).
            hl_tile = np.tile(self.hero_level, (1,1)).T
            ml_tile = multipliers.level_tile
            mb_tile = multipliers.bonus_tile
            level_check = (hl_tile>=ml_tile).argmin(axis=1) - 1
            self.hero_multiplier = mb_tile[:, level_check][0, :]

            # Hero skill multipliers.
            hi_tile = np.tile(heroes.id, (1,1)).T
            bi_tile = skills.bonus_id_tile
            bt_tile = skills.bonus_type_tile 
            bm_tile = skills.bonus_mult_tile 
            bl_tile = skills.bonus_level_tile

            # Hero level and hero id match condition.
            condition = ((hl_tile>=bl_tile)*(hi_tile==bi_tile))

            # Bonus effect matches.
            cd_match = (bt_tile[condition]=='CritDamage')
            cc_match = (bt_tile[condition]=='CritChance')
            bg_match = (bt_tile[condition]=='GoldBoss')
            ag_match = (bt_tile[condition]=='GoldAll')
            ad_match = (bt_tile[condition]=='AllDamage')
            ah_match = (bt_tile[condition]=='AllHelperDamage')
            md_match = (bt_tile[condition]=='MeleeHelperDamage')
            sd_match = (bt_tile[condition]=='SpellHelperDamage')
            rd_match = (bt_tile[condition]=='RangedHelperDamage')
            th_match = (bt_tile[condition]=='TapDamageFromHelpers')
            td_match = (bt_tile[condition]=='TapDamage')
            tg_match = (bt_tile[condition]=='GoldMonster')
            tx_match = (bt_tile[condition]=='Goldx10Chance')
            chc_match = (bt_tile[condition]=='ChestChance')
            chg_match = (bt_tile[condition]=='ChestAmount')

            # Apply bonuses.
            self.crit_damage = bm_tile[condition][cd_match].prod()
            self.crit_chance = min(SVM.maxCritChance,
                self.base_crit_chance+bm_tile[condition][cc_match].sum())
            self.boss_gold = self.base_boss_gold*bm_tile[condition][bg_match].prod()
            self.all_gold = self.base_all_gold*bm_tile[condition][ag_match].prod()
            self.all_damage = self.base_all_damage*bm_tile[condition][ad_match].prod()
            self.all_hero_damage = self.base_all_hero_damage*bm_tile[condition][ah_match].prod()
            self.melee_mult = self.base_melee_mult*bm_tile[condition][md_match].prod()
            self.spell_mult = self.base_spell_mult*bm_tile[condition][sd_match].prod()
            self.ranged_mult = self.base_ranged_mult*bm_tile[condition][rd_match].prod()
            self.chest_chance = self.base_chest_chance+bm_tile[condition][chc_match].sum()
            self.chest_gold = self.base_chest_gold*bm_tile[condition][chg_match].prod()
            self.titan_gold = self.base_titan_gold*bm_tile[condition][tg_match].prod()
            self.x10_gold_chance = self.base_x10_gold_chance+bm_tile[condition][tx_match].sum()
            self.tap_mult = self.base_tap_mult*bm_tile[condition][td_match].sum()
            self.tap_damage_from_hero = bm_tile[condition][th_match].sum()

    def calc_dps(self, heroes):
        # Update DPS only when heroes have been purchased or upgraded.
        if self.heroes_bought:

            # Calculate hero_dps for all heroes.
            hero_formula_id = np.minimum(heroes.unlock_order, SVM.maxHelperFormula)
            hero_efficiency = ((1 - SVM.helperInefficiency
                * np.minimum(hero_formula_id, SVM.helperInefficiencySlowDown))
                **hero_formula_id)
            self.hero_dps = (heroes.purchase_cost*SVM.dMGScaleDown*hero_efficiency
                * self.hero_level*self.hero_multiplier*self.all_damage
                * self.all_hero_damage*(1 + heroes.weapon_levels/2))

            # Apply damage type bonus and sum for total hero dps.
            self.hero_dps[heroes.melee_type] *= self.melee_mult
            self.hero_dps[heroes.spell_type] *= self.spell_mult
            self.hero_dps[heroes.ranged_type] *= self.ranged_mult

            self.total_hero_dps = self.hero_dps.sum()

            # Clan ship damage.
            self.ship_damage = (self.clan_size*SVM.clanShipDmgMult
                * (self.sword_master_level + self.total_hero_dps))

            # tap_with_average_crit is not the same as average tap damage.
            self.tap_damage = (self.sword_master_damage*self.tap_mult 
                + self.tap_damage_from_hero*self.total_hero_dps)
            self.tap_with_average_crit = (self.tap_damage
                * (1 + self.crit_chance*self.crit_damage
                    * (SVM.playerCritMinMult + SVM.playerCritMaxMult)/2)) 

            # Pet damage per attack and pet DPS.
            self.pet_damage_per_attack = max(self.tap_with_average_crit*self.pet_mult, 
                self.total_hero_dps)
            self.pet_dps = self.pet_rate*self.pet_damage_per_attack

            # Total DPS: flash zip assumes two full zips are completed during the fight.
            self.total_dps = (self.pet_dps + self.total_hero_dps 
                + self.ship_damage*SVM.clanShipAttackRate)
            self.total_boss_dps = self.total_dps + self.flash_zip*self.pet_damage_per_attack

        # Store total DPS and pet attack damage per stage.
        self.total_dps_array[self.stage] = self.total_dps
        self.pet_attack_damage_array[self.stage] = self.pet_damage_per_attack

    def fight_titans(self, stage):
        """
        The fight_titans method computes titan/chesterson gold from the current
        stage and stores the values.  Note that 10x gold does not couple with
        HoM pot gold.  Additional HoM coins are not computed here since they are
        negligable compared to the pot bonus.  Overkills due to splash/Tf are
        similarly not calculated since the gold gained per overkill multiplied
        with the average overkill chance is negligible compared to boss gold.
        """

        # Average Titan gold per stage:
        self.gold_array[self.stage, 1] = (stage.base_titan_gold[self.stage]
            * (stage.titan_count[self.stage])
            * (1-self.chest_chance)*self.titan_gold*self.all_gold
            * (1 + 9*self.x10_gold_chance + SVM.midasMultiplierNormal*self.hom))

        # Average Chesterson gold per stage:
        self.gold_array[self.stage, 2] = (stage.base_titan_gold[self.stage]
            * (stage.titan_count[self.stage])
            * self.chest_chance*self.chest_gold*self.all_gold*SVM.treasureGold
            * (1 + 9*self.x10_gold_chance + SVM.midasMultiplierChesterson*self.hom))

        # Add values to current_gold.
        self.current_gold += self.gold_array[self.stage, 1:].sum()

    def fight_boss(self, stage):
        """
        The fight_boss method just does a simple DPS*Time comparison against
        boss health to determine boss_kill.  Gold is awarded for a kill and
        the simulation loop is stopped otherwise.
        """

        # Boss kill condition.
        boss_kill = (self.total_boss_dps*self.boss_timer)>=stage.boss_hp[self.stage]

        if (self.stage==stage.cap or not boss_kill):
            self.end_simulation = True
        else:
            # Average Boss Gold:
            self.gold_array[self.stage, 0] = (stage.base_boss_gold[self.stage]
                * self.boss_gold*self.all_gold*SVM.maxBossGoldMultiplier
                * (1 + 9*self.x10_gold_chance + SVM.midasMultiplierBoss*self.hom))
            self.current_gold += self.gold_array[self.stage, 0]
            # Advance the current stage.
            self.stage += 1

    def finalize_results(self, data):
        """ Computes additional results after the sim has finished. """

        stage = data.stage
        heroes = data.heroes
        
        self.melee_dps = self.hero_dps[heroes.melee_type].sum()
        self.spell_dps = self.hero_dps[heroes.spell_type].sum()
        self.ranged_dps = self.hero_dps[heroes.ranged_type].sum()
       
        dps = self.total_dps_array

        # Stages clear durations.
        for i, s in enumerate([5, 15, 75]):
            stage_duration = (stage.number[(dps>0)*((s*dps)
                < (stage.titan_hp*stage.titan_count))])

            if stage_duration.any():
                self.stage_duration_stages[i] = stage_duration.min()


        if self.advanced_results:
            # Store splash results.
            damage_splashed = ((self.pet_attack_damage_array - stage.titan_hp)
                * self.splash_damage)

            for i, n in enumerate([1, 2, 3, 19]):
                # Maximum splash stages.
                max_splash = damage_splashed>n*stage.titan_hp
                if max_splash.any():
                    self.max_splash_stages[i] = stage.number[max_splash].max()
                # Continuous splash stages.
                cont_splash = ((self.total_dps_array>0)*(damage_splashed<n*stage.titan_hp))
                if cont_splash.any():
                    self.continuous_splash_stages[i] = stage.number[cont_splash].min()-1

            # Splash array of all max splash values.
            for i in range(20):
                self.splash_array[damage_splashed>(i+1)*stage.titan_hp] = (i+1)
                self.splash_array_penalty[damage_splashed>(i+1)*(2**i)*stage.titan_hp] = (i+1)

    def print_results(self, stage):
        print('\tGENERAL RESULTS:')
        print('\t\tFinal Stage:'.ljust(12), (str(self.stage)+',').rjust(5),
            ('Boss HP: '+letters(stage.boss_hp[self.stage], ',')).ljust(8),
            ('Damage: '
                + letters(self.total_boss_dps*self.boss_timer)).ljust(8))
        print('\t\tHero Levels:', self.hero_level[:8],
            '\n\t\t\t\t\t', self.hero_level[8:16], 
            '\n\t\t\t\t\t', self.hero_level[16:24], 
            '\n\t\t\t\t\t', self.hero_level[24:32], 
            '\n\t\t\t\t\t', self.hero_level[32:], 
            'Total:', self.hero_level.sum())

        c1, c2, c3, c4 = (13, 8, 15, 9)
        print('\n\tDAMAGE RESULTS:')
        print('\t\tTotal DPS:'.ljust(c1), 
            letters(self.total_dps).rjust(c2),
            '\t\tAll Bonus:'.ljust(c3), 
            letters(self.all_damage-1, '%').rjust(c4))
        print('\t\tHero DPS:'.ljust(c1), 
            letters(self.total_hero_dps).rjust(c2), 
            '\t\tHero Bonus:'.ljust(c3), 
            letters(self.all_hero_damage-1, '%').rjust(c4))
        print('\t\tMelee DPS:'.ljust(c1), 
            letters(self.melee_dps).rjust(c2),
            '\t\tMelee Bonus:'.ljust(c3), 
            letters(self.melee_mult-1, '%').rjust(c4))
        print('\t\tRanged DPS:'.ljust(c1), 
            letters(self.ranged_dps).rjust(c2),
            '\t\tRanged Bonus:'.ljust(c3), 
            letters(self.ranged_mult-1, '%').rjust(c4))
        print('\t\tSpell DPS:'.ljust(c1), 
            letters(self.spell_dps).rjust(c2),
            '\t\tSpell Bonus:'.ljust(c3), 
            letters(self.spell_mult-1, '%').rjust(c4))
        print('\t\tPet DMG:'.ljust(c1), 
            letters(self.pet_damage_per_attack).rjust(c2), 
            '\t\tPet Bonus:'.ljust(c3), 
            letters(self.pet_mult-1, '%').rjust(c4))
        print('\t\tTap DMG:'.ljust(c1), 
            letters(self.tap_damage).rjust(c2), 
            '\t\tTap Bonus:'.ljust(c3), 
            letters(self.tap_mult-1, '%').rjust(c4))
        print('\t\tShip DMG:'.ljust(c1), 
            letters(self.ship_damage).rjust(c2), 
            '\t\tClan Bonus:'.ljust(c3), 
            letters(self.clan_bonus-1, '%').rjust(c4))
        print('\t\tCrit Max:'.ljust(c1), 
            letters(SVM.playerCritMaxMult*self.crit_damage).rjust(c2), 
            '\t\tArtifact:'.ljust(c3), 
            letters(self.artifact_damage, '%').rjust(c4))
        print('\t\tCrit Min:'.ljust(c1), 
            letters(SVM.playerCritMinMult*self.crit_damage).rjust(c2),
            '\t\tCrit Chance:'.ljust(c3), 
            letters(self.crit_chance, '%').rjust(c4))
        
        c1, c2, c3, c4 = (15, 9, 11, 7)
        print('\n\tGOLD RESULTS:')
        print('\t\tTotal Earned:'.ljust(c1), 
            letters(self.gold_array.sum()).rjust(c2),
            '\tMultiplier:'.ljust(c3), 
            letters(self.all_gold).rjust(c4))
        print('\t\tBoss Gold:'.ljust(c1), 
            letters(self.gold_array[:,0].sum()).rjust(c2),
            '\tMultiplier:'.ljust(c3), 
            letters(self.boss_gold).rjust(c4))
        print('\t\tChest Gold:'.ljust(c1), 
            letters(self.gold_array[:,2].sum()).rjust(c2),
            '\tMultiplier:'.ljust(c3), 
            letters(self.chest_gold).rjust(c4))
        print('\t\tTitan Gold:'.ljust(c1), 
            letters(self.gold_array[:,1].sum()).rjust(c2),
            '\tMultiplier:'.ljust(c3), 
            letters(self.titan_gold).rjust(c4))
        print('\t\tRemaining:'.ljust(c1), 
            letters(self.current_gold).rjust(c2)) 
        print('\t\tSpent:'.ljust(c1), 
            letters(self.gold_spent).rjust(c2))

        c1, c2, c3, c4 = (18, 3, 6, 4)
        print('\n\tSTAGE COMPLETION TIMES (TITANS ONLY):')
        print('\t\t 5 Seconds Per Stage:'.ljust(c1),
            'Stage =', str(self.stage_duration_stages[0]).rjust(c4))
        print('\t\t15 Seconds Per Stage:'.ljust(c1),
            'Stage =', str(self.stage_duration_stages[1]).rjust(c4))
        print('\t\t75 Seconds Per Stage:'.ljust(c1),
            'Stage =', str(self.stage_duration_stages[2]).rjust(c4))

        if self.advanced_results:

            c1, c2, c3 = (5, 4, 4)
            print('\n\tSPLASH RESULTS (PET ATTACKS):')
            print('\t\tMaximum Splash Stage:'.ljust(27), 
                '\tx20:'.ljust(c1), str(self.max_splash_stages[3]).rjust(c2),
                '\tx4:'.ljust(c3), str(self.max_splash_stages[2]).rjust(c2), 
                '\n', '\t'*8,
                '\tx3:'.ljust(c1), str(self.max_splash_stages[1]).rjust(c2),
                '\tx2:'.ljust(c3), str(self.max_splash_stages[0]).rjust(c2))
            print('\t\tContinuous Splash Stage:'.ljust(27), 
                '\tx20:'.ljust(c1), str(self.continuous_splash_stages[3]).rjust(c2),
                '\tx4:'.ljust(c3), str(self.continuous_splash_stages[2]).rjust(c2), 
                '\n', '\t'*8,
                '\tx3:'.ljust(c1), str(self.continuous_splash_stages[1]).rjust(c2),
                '\tx2:'.ljust(c3), str(self.continuous_splash_stages[0]).rjust(c2))
            print('\t\tSplash Factor:', self.splash_damage)

            print('\n\tHERO EVOLVE STAGES:')
            print('\t\t1st Evolve: ', self.evolve1_stage[:8],
                '\n\t\t\t\t\t', self.evolve1_stage[8:16], 
                '\n\t\t\t\t\t', self.evolve1_stage[16:24], 
                '\n\t\t\t\t\t', self.evolve1_stage[24:32], 
                '\n\t\t\t\t\t', self.evolve1_stage[32:])
            print('\t\t2nd Evolve: ', self.evolve2_stage[:8],
                '\n\t\t\t\t\t', self.evolve2_stage[8:16], 
                '\n\t\t\t\t\t', self.evolve2_stage[16:24], 
                '\n\t\t\t\t\t', self.evolve2_stage[24:32], 
                '\n\t\t\t\t\t', self.evolve2_stage[32:])

    def measure_time(self):
        """ This is for optimization purposes. """
        if not self.time:
            self.time = time()
        else:
            print('\nSimulation Runtime:', '%.3fs'%(time()-self.time))


def run_simulation(input_csv, advanced_results=True):

    # Store all input and game data into single object.
    data = GameData(input_csv)

    # Initialize player object.
    player = Player(data, advanced_results)

    # Max-stage simulation:
    player.measure_time()
    while player.end_simulation is False:
        player.buy_heroes(data.heroes)
        player.hero_improvement_bonuses(data)
        player.calc_dps(data.heroes)
        player.fight_titans(data.stage)
        player.fight_boss(data.stage)

    player.finalize_results(data)
    player.print_results(data.stage)
    player.measure_time()
    return (player, data)

if __name__ == '__main__':
    player, data = run_simulation('PlayerInput_marzx13.csv')
    #plot_results(player, data.stage)
    plot_splash(player, data.stage)