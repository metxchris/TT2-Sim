from __future__ import division, print_function
import numpy as np
from math import modf
from copy import deepcopy
from DataClasses import GameData, notate, convert_time
from ServerVarsModel import SVM
import Plotting

"""
TT2-Sim by MetxChris.
Designed to run in Python 3.6+
This code reflects v1.4 of Tap Titans 2.

INSTRUCTIONS:
    Scroll down to the bottom and update the csv file name in
        player, stage = run_simulation('SwordMaster.csv')
    from 'SwordMaster.csv' to whatever you named your input csv.
    When using Sublime Text 3, run the code by going to the Tools menu up top
    and selecting the build option (Ctrl+B on windows).
    The output will display in a pop-in window at the bottom of Sublime Text 3.

1. Active Skills in Use:
    All active skills are put to use here.

2. Artifacts in Use:
    Most if not all artifacts other than the skill duration/skill cost
    artifacts should be referenced here.

3. Skill Tree Talents in Use:
    a. Yellow Tree: Flash Zip, Boss Timer.
    The remaining skills here are questionable at best and/or their
    effects aren't very well known. In particular, PET:HOM gives
    x5 the base monster gold amount at level 1 per proc, which is
    1/4 the amount of starting gold you get after prestige (for a
    given stage), so this is worthless.  The lightning burst skill
    also does basically nothing so that too is omitted.

    b. Green Tree: Pet Evo, Type Damages, IP, TF, ER.
    This is most of the green skills.  The remaining ones could be
    included for offline calculations at some point.

    c. Blue Tree: Heavenly Strike, Fire Sword, Heroic Might.
    The HoM skill deals damage equal to
    200*tap_with_average_crit once per skill activation, which
    is generally less than a single shadow clone strike, so this is
    intentionally omitted.  The Critical Strike lightning skill could be
    included if I were to derive a good model to approximate how much 
    damage it does on average per titan or boss. The SC tree upgrade is
    purely detrimental (although won't affect higher level players), so       
    this too is left out.

4. Equipment/Pet Bonuses in Use:
    All Equipment bonuses are used and All pet bonuses should be in play.
"""

class Player(object):

    # Measurement delay reflects the average update delay between when
    # attacks are registered within the actual game engine itself.
    measurement_delay = 0.05

    # These control what values are displayed in the printed results.
    splash_amounts = ([20, 4, 3, 2, 1])
    attack_durations = ([0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                         0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 3.0])

    def __init__(self, data):

        # Unpack data object.
        advanced = data.advanced
        pets = data.pets
        artifacts = data.artifacts
        equipment = data.equipment
        skill_tree = data.skill_tree
        heroes = data.heroes
        hero_skills = data.hero_skills
        active_skills = data.active_skills
        stage = data.stage
        sword_master = data.sword_master

        # Store Advanced Options.
        self.stage_cap = stage.cap
        self.hero_cap = advanced.hero_cap
        self.sword_master_cap = advanced.sword_master_cap
        self.scientific_notation = advanced.scientific_notation
        self.disable_sword_master = advanced.disable_sword_master
        self.disable_heroes = advanced.disable_heroes
        self.disable_clan_ship = advanced.disable_clan_ship

        # Pull general input values from player input CSV.
        start_idx = np.array([data.input[:, 0]=='GENERAL INPUT VALUES']).argmax()+1
        end_idx = np.array([data.input[start_idx:, 0]=='']).argmax()+1
        input_values = data.input[start_idx:end_idx, 0].astype(np.float)
        input_type = data.input[start_idx:end_idx, 1]

        def get_player_input(input_name):
            # Avoids crashes if new input variables are missing.
            if (input_type==input_name).any():
                value = input_values[input_type==input_name][0]
            else:
                value = 0
                print('WARNING: Missing player input value for:', input_name)
                print(' '*8,'Please update your input csv to the most recent version.\n')
            return value

        # Store player input values.
        self.clan_level = get_player_input('ClanLevel')
        self.start_stage = min(max(get_player_input('StartStage'), 1), 
            self.stage_cap).astype(np.int)
        self.taps_sec = min(get_player_input('TapsPerSec'), 20)
        self.clan_size = min(get_player_input('ClanSize'), 50).astype(np.int)
        self.transition_delay = max(get_player_input('TransitionScreenDelay'), 0.3)
        self.device_lag = get_player_input('DeviceLag')
        self.username = data.username

        # Misc calculations.
        self.evolve1_stage = np.zeros_like(heroes.level)
        self.evolve2_stage = np.zeros_like(heroes.level)
        self.max_splash_stages = np.zeros_like(self.splash_amounts, dtype=np.int)
        self.min_splash_stages = np.zeros_like(self.splash_amounts, dtype=np.int)
        self.splash_array = np.zeros_like(stage.number, dtype=np.int)

        # Output performance arrays (attacks, duration).
        self.general_attacks = np.zeros((len(self.attack_durations), stage.number.size))
        self.active_time = np.zeros((len(self.attack_durations), stage.number.size))
        self.wasted_time = np.zeros((len(self.attack_durations), stage.number.size))
        self.regen_performance = np.zeros((len(self.attack_durations), stage.number.size))
        self.siphon_performance = np.zeros((len(self.attack_durations), stage.number.size))
        self.manni_performance = np.zeros((len(self.attack_durations), stage.number.size))
        self.general_performance = np.zeros((len(self.attack_durations), 3))
        self.pet_performance = np.zeros(3, dtype=np.float)
        self.hs_performance = np.zeros(3, dtype=np.float)
        self.tap_performance = np.zeros(3, dtype=np.float)

        # Initialize Default Values.
        self.hero_level = heroes.level
        self.hero_dps = np.zeros_like(self.hero_level, dtype=np.float)
        self.default_levels_to_buy = (advanced.levels_to_buy
            * np.ones_like(heroes.level).astype(np.int))
        self.hero_multiplier = np.zeros_like(heroes.level, dtype=np.float)
        self.sword_master_bought = False
        self.heroes_bought = False
        self.end_simulation = False

        # Initialize variables to be updated later.
        self.sword_master_damage = 0
        self.sword_master_level = 0
        self.pet_damage_per_attack = 0
        self.tap_from_hero = 0
        self.tap_with_average_crit = 0
        self.average_tap_damage = 0
        self.tap_damage = 0
        self.ship_damage = 0
        self.melee_dps = 0
        self.spell_dps = 0
        self.ranged_dps = 0
        self.pet_dps = 0
        self.tap_dps = 0
        self.total_dps = 0
        self.total_boss_dps = 0
        self.shadow_clone_dps = 0
        self.gold_spent = 0

        # Values stored for each stage.
        self.relic_efficiency = np.zeros_like(self.active_time)
        self.pet_attack_damage_array = np.zeros_like(stage.number, dtype=np.float)
        self.tap_with_avg_crit_array = np.zeros_like(stage.number, dtype=np.float)
        self.tap_damage_array = np.zeros((stage.number.size, 2), dtype=np.float)
        self.total_dps_array = np.zeros((stage.number.size, 2), dtype=np.float)
        self.hero_dps_array = np.zeros_like(stage.number, dtype=np.float)
        self.tap_dps_array = np.zeros_like(stage.number, dtype=np.float)
        self.gold_array = np.zeros((stage.number.size, 3), dtype=np.float)
        self.mana_capacity_array = np.zeros_like(stage.number, dtype=np.float)
        self.mana_regen_array = np.zeros_like(stage.number, dtype=np.float)
        self.mana_siphon_array = np.zeros_like(stage.number, dtype=np.float)
        self.transition_array =  np.zeros_like(stage.number)

        # Clan Quest Bonus.
        self.clan_bonus = max(1, (SVM.clanBonusBase
            **min(self.clan_level, SVM.clanQuestStageNerf)
            * SVM.clanBonusBaseNerf
            **max(self.clan_level - SVM.clanQuestStageNerf, 0) 
            * (1 - advanced.disable_clan_bonus)))

        # Initialize active skill bonuses. Heavenly Strike active skill is 
        # only used for goofy time-table calc.
        self.heavenly_strike = active_skills.effects[0]*artifacts.hs_bonus
        self.crit_strike = active_skills.effects[1]
        self.hom = active_skills.effects[2]*artifacts.hom_bonus
        self.fire_sword = max(1, active_skills.effects[3]*artifacts.fs_bonus)
        self.war_cry = max(1, active_skills.effects[4]*artifacts.wc_bonus)
        self.shadow_clone = active_skills.effects[5]*artifacts.sc_bonus
        self.mana_costs = active_skills.mana_costs
        self.skill_durations = active_skills.durations
        self.skill_cooldowns = active_skills.cooldowns
        self.skill_levels = active_skills.levels
        
        # War Cry Skill Tree Upgrade (This boosts avg DPS but not displayed DPS)
        # Heroes have 10% chance to crit during WC with Heroic Might.
        if (skill_tree.wc_bonus and self.war_cry>1):
            self.war_cry_talent = 0.9+0.1*skill_tree.wc_bonus
        else:
            self.war_cry_talent = 1

        # Additive skill-tree bonuses.
        if self.heavenly_strike>1:
            self.heavenly_strike += artifacts.hs_bonus*skill_tree.hs_bonus
        if self.fire_sword>1:
            self.fire_sword += artifacts.fs_bonus*skill_tree.fs_bonus

        self.active_skills = np.array([self.crit_strike, self.hom, self.fire_sword, 
            self.war_cry, self.shadow_clone])

        # Pet damage multiplier.
        self.pet_mult = (pets.damage_mult*artifacts.pet_damage
            * skill_tree.pet_damage*equipment.pet_damage)

        # Pet auto-attack and attack-rate.
        self.pet_auto = 1 if (pets.level.sum()>=SVM.petAutoAttackLevel) else 0
        self.pet_rate = (self.taps_sec/SVM.tapsPerSecond
            + self.pet_auto/SVM.petAutoAttackDuration)*(1-advanced.disable_pet_attack)

        # Skill tree values; flash_zip requires tapping.
        self.flash_zip = skill_tree.flash_zip*(self.taps_sec>0)
        self.boss_timer = 30 + skill_tree.boss_timer

        # Artifact damage multiplier.
        self.artifact_damage = artifacts.total_damage

        # Damage type multipliers
        self.base_all_damage = (pets.all_damage*artifacts.all_damage
            * equipment.all_damage*self.clan_bonus*self.artifact_damage
            * heroes.set_bonus)
        self.base_all_hero_damage = (pets.all_hero_damage
            *artifacts.all_hero_damage* equipment.all_hero_damage*self.war_cry)
        self.base_melee_mult = (pets.melee_damage*artifacts.melee_damage
            * skill_tree.melee_damage*equipment.melee_mult)
        self.base_spell_mult = (pets.spell_damage*artifacts.spell_damage
            * skill_tree.spell_damage*equipment.spell_mult)
        self.base_ranged_mult = (pets.ranged_damage*artifacts.ranged_damage
            * skill_tree.ranged_damage*equipment.ranged_mult)
        self.base_tap_mult = (pets.tap_damage*artifacts.tap_damage
            * equipment.tap_damage) 
        self.splash_damage = pets.splash_damage+skill_tree.splash_damage
        self.base_crit_chance = (SVM.playerCritChance+artifacts.crit_chance
            + equipment.crit_chance/100 + self.crit_strike)

        # Gold multipliers.
        self.base_all_gold = pets.all_gold*artifacts.all_gold*equipment.all_gold
        self.base_titan_gold = artifacts.titan_gold
        self.base_boss_gold = artifacts.boss_gold
        self.base_chest_gold = artifacts.chest_gold*equipment.chest_gold
        self.base_chest_chance = (artifacts.chest_chance 
            + equipment.chest_chance/100 + SVM.chestersonChance)
        self.base_x10_gold_chance = SVM.goldx10Chance + artifacts.x10_gold_chance
        self.tf_chance = 0.01 + skill_tree.tf_chance
        self.tf_bonus = 1 + 2.5*self.tf_chance
        self.cost_reduction = artifacts.cost_reduction

        # Mana bonuses.
        self.base_mana_regen = 2 + pets.mana_regen + skill_tree.mana_regen 
        self.mana_siphon = skill_tree.mana_siphon/100
        self.base_mana_capacity = 35*6 + skill_tree.mana_capacity
        self.manni_mana = skill_tree.manni_mana

        # Starting gold (gives 20x titan gold from current stage with min = 30 gold)
        self.stage = self.start_stage
        self.current_gold = max((20*stage.base_titan_gold[self.stage]
            *self.base_titan_gold*self.base_all_gold), 30)

        # Final initializations. These are overwritten in hero_improvement_bonuses(),
        # but are needed if heroes are disabled.
        self.sword_master_mult = 1
        self.crit_damage = 1
        self.crit_chance = min(SVM.maxCritChance, self.base_crit_chance)
        self.boss_gold = self.base_boss_gold
        self.all_gold = self.base_all_gold
        self.all_damage = self.base_all_damage
        self.all_hero_damage = self.base_all_hero_damage
        self.melee_mult = self.base_melee_mult
        self.spell_mult = self.base_spell_mult
        self.ranged_mult = self.base_ranged_mult
        self.chest_chance = self.base_chest_chance
        self.chest_gold = self.base_chest_gold
        self.titan_gold = self.base_titan_gold
        self.x10_gold_chance = self.base_x10_gold_chance
        self.tap_mult = self.base_tap_mult
        self.mana_capacity = self.base_mana_capacity
        self.mana_regen = self.base_mana_regen


    def buy_sword_master(self, sword_master):
        """ Buys Sword Master levels and updates the damage multiplier. """

        # Advanced Option
        if self.disable_sword_master:
            return

        self.sword_master_bought, keep_buying = (False, True)
        while (keep_buying and self.sword_master_level<self.sword_master_cap):

            levels_to_buy = self.default_levels_to_buy[0]
            level_cost =  (SVM.playerUpgradeCostBase 
                * (SVM.playerUpgradeCostGrowth
                    ** (self.sword_master_level + levels_to_buy) 
                    - SVM.playerUpgradeCostGrowth**self.sword_master_level) 
                / (SVM.playerUpgradeCostGrowth - 1))

            # Gold check.
            keep_buying = self.current_gold>=level_cost

            if keep_buying:
                # Sword Master levels are free until they are worth buying.
                self.sword_master_level += levels_to_buy
                self.sword_master_bought = True

        if self.sword_master_bought:
            # Updates the improvement bonus multiplier.
            sm_mult = sword_master.multipliers
            sm_level = sword_master.levels
            self.sword_master_mult = (self.base_tap_mult
                * sm_mult[self.sword_master_level>=sm_level].max())


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

        # Advanced Option
        if self.disable_heroes:
            return

        # Reset hero level purchase tracking.
        self.heroes_bought = False

        # Abbreviate self.hero_level to use below.
        level = self.hero_level

        # Attempt to unlock heroes until all heroes are purchased.
        if (level.min()==0):
            gold_check = (self.current_gold
                >= (1-self.cost_reduction)*heroes.purchase_cost)

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
            level_cost[(level==999)+(level==1999)] *= SVM.evolveCostMultiplier

            # Store evolve levels for each hero.
            evolve1_level_check = (self.evolve1_stage==0)*(level==1000)
            evolve2_level_check = (self.evolve2_stage==0)*(level==2000)
            self.evolve1_stage[evolve1_level_check] = self.stage
            self.evolve2_stage[evolve2_level_check] = self.stage

            # Apply level gain.  (level_cost==0 implies levels_to_buy==0).
            gold_check = self.current_gold>=level_cost
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
        a stage early won't make much of a difference.  The game also gives 
        these out for free for each hero that has a weapon upgrade.
        """

        if not self.heroes_bought:
            return

        heroes = data.heroes
        skills = data.hero_skills
        multipliers = data.hero_improvements
    
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

        # Hero level check and hero id match condition.
        condition = ((hl_tile>=bl_tile)*(hi_tile==bi_tile))

        # Skill effect matches.
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
        mp_match = (bt_tile[condition]=='ManaPoolCap')
        mg_match = (bt_tile[condition]=='ManaRegen')
        chc_match = (bt_tile[condition]=='ChestChance')
        chg_match = (bt_tile[condition]=='ChestAmount')

        # Skill effect values.
        tap_from_hero = bm_tile[condition][th_match].sum()
        crit_damage = bm_tile[condition][cd_match].prod()
        crit_chance = bm_tile[condition][cc_match].sum()
        boss_gold = bm_tile[condition][bg_match].prod()
        all_gold = bm_tile[condition][ag_match].prod()
        all_damage = bm_tile[condition][ad_match].prod()
        all_hero_damage = bm_tile[condition][ah_match].prod()
        melee_damage = bm_tile[condition][md_match].prod()
        spell_damage = bm_tile[condition][sd_match].prod()
        ranged_damage = bm_tile[condition][rd_match].prod()
        chest_chance = bm_tile[condition][chc_match].sum()
        chest_gold = bm_tile[condition][chg_match].prod()
        titan_gold = bm_tile[condition][tg_match].prod()
        x10_chance = bm_tile[condition][tx_match].sum()
        tap_damage = bm_tile[condition][td_match].prod()
        mana_pool = bm_tile[condition][mp_match].sum()
        mana_regen = bm_tile[condition][mg_match].sum()

        # Combine skill bonuses from heroes with base values.
        self.boss_gold = self.base_boss_gold*boss_gold
        self.all_gold = self.base_all_gold*all_gold
        self.all_damage = self.base_all_damage*all_damage
        self.all_hero_damage = self.base_all_hero_damage*all_hero_damage
        self.melee_mult = self.base_melee_mult*melee_damage
        self.spell_mult = self.base_spell_mult*spell_damage
        self.ranged_mult = self.base_ranged_mult*ranged_damage
        self.chest_chance = self.base_chest_chance+chest_chance
        self.chest_gold = self.base_chest_gold*chest_gold
        self.titan_gold = self.base_titan_gold*titan_gold
        self.x10_gold_chance = self.base_x10_gold_chance+x10_chance
        self.tap_mult = self.base_tap_mult*tap_damage
        self.tap_from_hero = tap_from_hero
        self.crit_damage = crit_damage
        self.crit_chance = min(SVM.maxCritChance, 
                                self.base_crit_chance+crit_chance)
        self.mana_capacity = self.base_mana_capacity + mana_pool
        self.mana_regen = self.base_mana_regen + mana_regen

    def calc_dps(self, heroes):
        # Update DPS only when heroes have been purchased or upgraded.
        if (self.heroes_bought or self.sword_master_bought):

            # Calculate hero_dps for all heroes.
            hero_formula_id = np.minimum(heroes.unlock_order, SVM.maxHelperFormula)
            hero_efficiency = ((1 - SVM.helperInefficiency
                * np.minimum(hero_formula_id, SVM.helperInefficiencySlowDown))
                **hero_formula_id)
            self.hero_dps = (heroes.purchase_cost*SVM.dMGScaleDown*hero_efficiency
                * self.hero_level*self.hero_multiplier*self.all_damage
                * self.all_hero_damage*heroes.weapon_bonus)
            # Apply damage type bonus and sum for total hero dps.
            self.hero_dps[heroes.melee_type] *= self.melee_mult
            self.hero_dps[heroes.spell_type] *= self.spell_mult
            self.hero_dps[heroes.ranged_type] *= self.ranged_mult

            self.total_hero_dps = self.hero_dps.sum()

            # Clan ship damage.
            self.ship_damage = (self.clan_size*SVM.clanShipDmgMult
                * (self.sword_master_level + self.total_hero_dps)
                * (1 - self.disable_clan_ship))

            # Tap damage.
            self.sword_master_damage = (self.sword_master_level
                * self.sword_master_mult*SVM.playerDamageMult
                * self.tap_mult*self.all_damage)
            self.tap_damage = (self.sword_master_damage
                + self.tap_from_hero*self.total_hero_dps)
            # tap_with_average_crit is not the same as average tap damage.
            self.tap_with_average_crit = (self.tap_damage
                * (1 + self.crit_chance*self.crit_damage
                    * (SVM.playerCritMinMult + SVM.playerCritMaxMult)/2))
            self.average_tap_damage = (self.tap_damage*self.fire_sword
                * (1 - self.crit_chance + self.crit_chance*self.crit_damage
                    * (SVM.playerCritMinMult + SVM.playerCritMaxMult)/2))
            self.tap_dps = self.average_tap_damage*self.taps_sec

            # Pet damage per attack and pet DPS.
            self.pet_damage_per_attack = max(self.tap_with_average_crit
                * self.pet_mult, self.total_hero_dps)
            self.pet_dps = self.pet_rate*self.pet_damage_per_attack

            self.shadow_clone_dps = self.tap_with_average_crit*self.shadow_clone

            # war_cry_talent needs to go here specifically.  It boosts avg hero damage only.
            self.total_dps = (self.pet_dps + self.total_hero_dps*self.war_cry_talent
                + self.tap_dps + self.ship_damage/SVM.clanShipAttackRate 
                + self.shadow_clone_dps)
            # Total Boss DPS: flash zip assumes two full zips are completed.
            self.total_boss_dps = (self.total_dps 
                + self.flash_zip*self.pet_damage_per_attack)

        # Store total DPS and pet attack damage per stage.
        self.total_dps_array[self.stage] = self.total_dps, self.total_boss_dps
        self.hero_dps_array[self.stage] = self.total_hero_dps
        self.pet_attack_damage_array[self.stage] = self.pet_damage_per_attack
        self.tap_dps_array[self.stage] = self.tap_dps
        self.tap_with_avg_crit_array[self.stage] = self.tap_with_average_crit
        self.tap_damage_array[self.stage] = (
            (self.tap_from_hero*self.total_hero_dps)*self.fire_sword, 
            self.sword_master_damage*self.fire_sword)
        self.mana_capacity_array[self.stage] = self.mana_capacity
        self.mana_regen_array[self.stage] = self.mana_regen

    def fight_titans(self, stage):
        """
        The fight_titans method computes titan/chesterson gold from the current
        stage and stores the values.  Note that 10x gold does not couple with
        HoM pot gold.  Additional HoM coins are not computed here since they are
        negligable compared to the pot bonus.  Overkills due to splash are
        similarly not calculated since the additional computational time to 
        calculate this per stage is not worth the resulting negligible increase
        in non-boss gold per stage. The bonus for TF is taken from the inactive
        gold model in the game files.  While this matches the inactive model,
        the form of the bonus is an overestimation of it's worth, so it should be
        compensated by a reducing factor at some point (to be determined here).
        """

        # Average Titan gold per stage:
        self.gold_array[self.stage, 1] = (stage.base_titan_gold[self.stage]
            * (stage.titan_count[self.stage])
            * (1-self.chest_chance)*self.titan_gold*self.all_gold
            * (1 + 9*self.x10_gold_chance + self.tf_bonus 
                + SVM.midasMultiplierNormal*self.hom))

        # Average Chesterson gold per stage:
        self.gold_array[self.stage, 2] = (stage.base_titan_gold[self.stage]
            * (stage.titan_count[self.stage])*self.tf_bonus
            * self.chest_chance*self.chest_gold*self.all_gold*SVM.treasureGold
            * (1 + 9*self.x10_gold_chance + self.tf_bonus 
                + SVM.midasMultiplierChesterson*self.hom))

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

        stage, heroes = data.stage, data.heroes

        def performance_analysis(base_attack_duration, dps, use_zip):
            """
            Here we calculate attacks made and time spent on each stage, using
            stored dps values from the simulation loop.  The use_zip option
            allows flash_zip to be considered or disabled; the flash_zip section
            below is equivalent to a normal boss fight when use_zip = 0. 
            zip_equivalent is used to convert the number of pet attacks reduced
            by flash zip into the number of input attacks reduced as per input dps.  
            """
            
            domain = (dps>0)*(stage.number<self.stage)
            step_size = 0.01
            max_measurement_delay = self.measurement_delay + step_size

            # The max value used by the range is max_measurement_delay - step_size
            measurement_range = np.arange(0, max_measurement_delay, step_size)
            attack_count_array = np.zeros((dps[domain].size, measurement_range.size))
            active_time_array = np.zeros_like(attack_count_array)
            wasted_time_array = np.zeros_like(attack_count_array)

            # Average over a range of delays to reflect in-game imperfections.
            # Doesn't seem like much of a bottleneck so left it in loop form.
            for i, measurement_delay in enumerate(measurement_range):
                delay_per_spawn = (SVM.killAnimationTime + measurement_delay
                     + self.device_lag)
                attack_duration = base_attack_duration
                attack_rate = 1/attack_duration

                # Reduced Titan counts and equivalent attacks as per splash reduction.
                attack_damage = dps[domain]/attack_rate
                damage_splashed = np.maximum(0, 
                    attack_damage-stage.titan_hp[domain])*self.splash_damage
                splash_factor = np.floor(np.minimum(3, 
                    damage_splashed/stage.titan_hp[domain]))+1
                remaining_titans = np.ceil(stage.titan_count[domain]/splash_factor)
                attacks_per_titan = (np.ceil(
                     np.maximum(1, stage.titan_hp[domain]/attack_damage)))
                # Boss attack counting.
                attacks_required = np.ceil(stage.boss_hp[domain]/attack_damage)
                attacks_per_boss = np.zeros_like(attacks_required)
                # Count attacks made before first zip occurs at 10sec.
                flash_zip_delay = 10
                attacks_before_delay = np.floor(flash_zip_delay*attack_rate)
                attacks_per_boss = np.minimum(attacks_before_delay, attacks_required)
                # Subtract the zip; Each zip level counts as zip_equivalent attacks.
                zip_equivalent = use_zip*np.floor(15*self.flash_zip
                    * self.pet_attack_damage_array[domain]/attack_damage)
                attacks_remaining = np.maximum(0, 
                    attacks_required-attacks_per_boss - zip_equivalent)
                # Sum the remaining attacks up until the second zip at 30sec.
                attacks_until_next_zip = np.minimum(attacks_remaining, 
                    2*attacks_before_delay)
                attacks_per_boss += attacks_until_next_zip
                attacks_remaining -= attacks_until_next_zip
                # Subtract second zip and sum remaining attacks. There are only remaining
                # attacks after the 2nd zip for goofy calculations like Heavenly Strike.
                attacks_per_boss += np.maximum(0, attacks_remaining - zip_equivalent)
                # Attack times with an offset for the first attack made vs. each monster.
                first_attack_delay = np.abs(np.maximum(1, 
                    np.ceil(delay_per_spawn*attack_rate))/attack_rate
                        - delay_per_spawn)
                time_per_titan = (first_attack_delay
                    + (attacks_per_titan - 1)*(attack_duration))
                time_per_boss = (first_attack_delay  
                    + (attacks_per_boss - 1)*(attack_duration))
                # Compute total times and attacks.
                attack_count_array[:, i] = (attacks_per_titan*remaining_titans
                    + attacks_per_boss)
                active_time_array[:, i] = ((time_per_titan - measurement_delay)
                    * remaining_titans + time_per_boss)
                wasted_time_array[:, i] = ((delay_per_spawn + measurement_delay)
                    * (remaining_titans + 1))

            # Average values over the measurement range.
            avg_attack_count = attack_count_array.sum(axis=1)/measurement_range.size
            avg_active_time = active_time_array.sum(axis=1)/measurement_range.size
            avg_wasted_time = wasted_time_array.sum(axis=1)/measurement_range.size
            return(avg_attack_count, avg_active_time, avg_wasted_time, remaining_titans)

        # Damage type dps for output display.
        self.melee_dps = self.hero_dps[heroes.melee_type].sum()
        self.spell_dps = self.hero_dps[heroes.spell_type].sum()
        self.ranged_dps = self.hero_dps[heroes.ranged_type].sum()

        attack_dps = self.total_dps_array[:, 0]
        domain = (attack_dps>0)*(stage.number<self.stage)
        self.transition_array[domain] = self.transition_delay*stage.transitions[domain]
        transition_time = self.transition_array.sum()

        # Main Performance loop, calculate attacks and times of attack_durations.
        # We fix DPS per stage and alter attack rate to get dmg per attack.
        for i, attack_duration in enumerate(self.attack_durations):
            attacks, active, wasted, titans = performance_analysis(attack_duration,
                                                                   attack_dps,
                                                                   1)
            # Summed values used for printed output.
            self.general_performance[i, 0] = attacks.sum()
            self.general_performance[i, 1] = active.sum()
            self.general_performance[i, 2] = wasted.sum() + transition_time
            # Arrays used for calculations and plotting.
            self.general_attacks[i, domain] = attacks
            self.active_time[i, domain] = active
            self.wasted_time[i, domain] = wasted
            # Manni Mana performance
            self.manni_performance[i, domain] = SVM.manaMonsterChance*titans*self.manni_mana

        # Mana Regen/Siphon performance
        self.regen_performance = (self.mana_regen_array*(self.active_time
            +self.wasted_time+self.transition_array))/60
        self.siphon_performance = (SVM.chanceForManaSteal*self.mana_capacity_array
            *self.taps_sec*(self.active_time+self.wasted_time)*self.mana_siphon)

        # Pet Performance.
        if self.pet_rate:
            attack_dps = self.pet_attack_damage_array*self.pet_rate
            attacks, active, wasted, __ = performance_analysis(1/self.pet_rate,
                                                               attack_dps,
                                                               1)
            self.pet_performance[0] = attacks.sum()
            self.pet_performance[1] = active.sum()
            self.pet_performance[2] = wasted.sum() + transition_time

        # Tap Performance
        if self.taps_sec:
            attacks, active, wasted, __ = performance_analysis(1/self.taps_sec,
                                                               self.tap_dps_array,
                                                               0)
            self.tap_performance[0] = attacks.sum()
            self.tap_performance[1] = active.sum()
            self.tap_performance[2] = wasted.sum() + transition_time

        # Really important Heavenly Strike performance.
        if self.heavenly_strike>1:
            strike_duration = self.skill_durations[0] + self.skill_cooldowns[0]
            strike_dps = (self.heavenly_strike
                * self.tap_with_avg_crit_array/strike_duration)
            attacks, active, wasted, __ = performance_analysis(strike_duration,
                                                               strike_dps,
                                                               0)
            self.hs_performance[0] = attacks.sum()
            self.hs_performance[1] = active.sum()
            self.hs_performance[2] = wasted.sum() + transition_time

        # Record splash results.
        damage_splashed = np.maximum(0, self.splash_damage
            * (self.pet_attack_damage_array-stage.titan_hp))
        self.splash_array = np.floor(damage_splashed/stage.titan_hp)

        for i, splash_value in enumerate(self.splash_amounts):
            max_splash = stage.number[self.splash_array>splash_value]
            if max_splash.any():
                self.max_splash_stages[i] = max_splash.max()
            condition = (self.splash_array>0)*(self.splash_array<splash_value+1)
            min_splash = stage.number[condition]
            if min_splash.any():
                self.min_splash_stages[i] = min_splash.min()-1

        # Prestige Relic Efficiency.
        domain = (attack_dps>0)
        interval_idx = 4
        total_time = (self.active_time[:, domain] 
            + self.wasted_time[:, domain] + self.transition_array[domain])
        base_relics = stage.relics[self.start_stage]
        summed_time = np.zeros(len(self.attack_durations))
        if total_time[0, :].sum():
            for i, __ in enumerate(total_time[0, :]):
                j = i + self.start_stage
                summed_time += total_time[:, i]
                self.relic_efficiency[:, j] = (stage.relics[j]-base_relics)/summed_time


    def print_results(self, stage, silent_output):
        """
        I use the '\t'+string syntax below to make sure that tabs
        aren't included in the left/right justification.
        """

        if silent_output:
            return

        N = self.scientific_notation

        c1, c2 = (4, 8)
        hline = '\t'+'\u2015'*(c1+c2+29)
        hline2 = '\t'+'\u2015'*(c1+c2+42)
        print('\t'+'GENERAL RESULTS FOR:', self.username)
        print(hline)
        print('\t'+'Final Stage:', str(self.stage).rjust(c1),
            '\t\t'+'Boss HP:',
            notate(stage.boss_hp[self.stage], N).rjust(c2))
        print('\t'+'Start Stage:', str(self.start_stage).rjust(c1),
            '\t\t'+'Damage: ',
            notate(self.total_boss_dps*self.boss_timer, N).rjust(c2))
        if self.hero_level.max():
            print(hline2)
            print('\t'+'Hero Levels:', self.hero_level[:8],
                '\n\t\t\t\t', self.hero_level[8:16], 
                '\n\t\t\t\t', self.hero_level[16:24], 
                '\n\t\t\t\t', self.hero_level[24:32], 
                '\n\t\t\t\t', self.hero_level[32:], 
                'Total:', self.hero_level.sum())

        if self.active_skills.sum()>2:
            c1, c2, c3 = (13, 9, 13)
            hline = '\t'+'\u2015'*(c1+c2+c3+2)
            print('\n\n\t'+'ACTIVE SKILL INFO:')
            print(hline)
            print('\t'+'Name'.ljust(c1),
                '    Level'.ljust(c2),
                '      Effect'.ljust(c3))
            print(hline)
            if self.crit_strike:
                print('\t'+'Crit Strike'.ljust(c1), 
                    str(self.skill_levels[1]).rjust(c2),
                    notate(self.crit_strike, N, '%').rjust(c3))
            if self.hom:
                print('\t'+'Hand of Midas'.ljust(c1), 
                    str(self.skill_levels[2]).rjust(c2),
                    notate(self.hom, N).rjust(c3))
            if self.fire_sword>1:
                print('\t'+'Fire Sword'.ljust(c1), 
                    str(self.skill_levels[3]).rjust(c2),
                    notate(self.fire_sword, N).rjust(c3))        
            if self.war_cry>1:
                print('\t'+'War Cry'.ljust(c1), 
                    str(self.skill_levels[4]).rjust(c2),
                    notate(self.war_cry, N).rjust(c3))
            if self.shadow_clone:
                print('\t'+'Shadow Clone'.ljust(c1), 
                    str(self.skill_levels[5]).rjust(c2),
                    notate(self.shadow_clone, N).rjust(c3))
            print(hline)

        c1, c2, c3 = (12, 12, 13)
        hline = '\t'+'\u2015'*(c1+c2+c3+2)
        print('\n\n\t'+'DAMAGE RESULTS:')
        print(hline)
        print('\t'+'Type'.ljust(c1),
            '   Amount'.ljust(c2),
            '    Bonus'.ljust(c3))
        print(hline)
        print('\t'+'Total DPS'.ljust(c1), 
            notate(self.total_dps, N).rjust(c2),
            notate(self.all_damage-1, N, '%').rjust(c3))
        print('\t'+'Hero DPS'.ljust(c1), 
            notate(self.total_hero_dps, N).rjust(c2), 
            notate(self.all_hero_damage-1, N, '%').rjust(c3))
        print('\t'+'Melee DPS'.ljust(c1), 
            notate(self.melee_dps, N).rjust(c2),
            notate(self.melee_mult-1, N, '%').rjust(c3))
        print('\t'+'Ranged DPS'.ljust(c1), 
            notate(self.ranged_dps, N).rjust(c2),
            notate(self.ranged_mult-1, N, '%').rjust(c3))
        print('\t'+'Spell DPS:'.ljust(c1), 
            notate(self.spell_dps, N).rjust(c2),
            notate(self.spell_mult-1, N, '%').rjust(c3))
        print('\t'+'Pet DMG:'.ljust(c1), 
            notate(self.pet_damage_per_attack, N).rjust(c2), 
            notate(self.pet_mult-1, N, '%').rjust(c3))
        print('\t'+'Tap DMG:'.ljust(c1), 
            notate(self.tap_damage*self.fire_sword, N).rjust(c2), 
            notate(self.tap_mult-1, N, '%').rjust(c3))
        print('\t'+'Clan DMG:'.ljust(c1), 
            notate(self.ship_damage, N).rjust(c2), 
            notate(self.clan_bonus-1, N, '%').rjust(c3))
        print(hline)
        print('\t'+'Crit Chance:'.ljust(c1),
            ''.ljust(c2),
            notate(self.crit_chance, N, '%').rjust(c3))
        print('\t'+'Crit Max:'.ljust(c1), 
            notate(SVM.playerCritMaxMult*self.crit_damage, N).rjust(c2),)
        print('\t'+'Crit Min:'.ljust(c1), 
            notate(SVM.playerCritMinMult*self.crit_damage, N).rjust(c2))
        print(hline)
        print('\t'+'Artifact DMG:'.ljust(c1), 
            ''.ljust(c2),
            notate(self.artifact_damage, N, '%').rjust(c3))
        
        c1, c2, c3 = (16, 8, 13)
        hline = '\t'+'\u2015'*(c1+c2+c3+2)
        print('\n\n\t'+'GOLD RESULTS:')
        print(hline)
        print('\t'+'Type'.ljust(c1),
            'Amount'.ljust(c2),
            'Multiplier'.rjust(c3))
        print(hline)
        print('\t'+'Total Earned'.ljust(c1), 
            notate(self.gold_array.sum(), N).rjust(c2),
            notate(self.all_gold, N).rjust(c3))
        print('\t'+'Boss Gold'.ljust(c1), 
            notate(self.gold_array[:,0].sum(), N).rjust(c2),
            notate(self.boss_gold, N).rjust(c3))
        print('\t'+'Chest Gold'.ljust(c1), 
            notate(self.gold_array[:,2].sum(), N).rjust(c2),
            notate(self.chest_gold, N).rjust(c3))
        print('\t'+'Titan Gold'.ljust(c1), 
            notate(self.gold_array[:,1].sum(), N).rjust(c2),
            notate(self.titan_gold, N).rjust(c3))
        print('\t'+'TF Chance'.ljust(c1), 
            notate(self.tf_chance, N, '%').rjust(c2),
            notate(self.tf_bonus, N).rjust(c3),
            '\u2020')
        print('\t'+'10x Chance'.ljust(c1), 
            notate(self.x10_gold_chance, N, '%').rjust(c2),
            notate(1 + 9*self.x10_gold_chance, N).rjust(c3),
            '\u2021')
        print(hline)
        print('\t'+'Remaining'.ljust(c1), 
            notate(self.current_gold, N).rjust(c2)) 
        print('\t'+'Spent'.ljust(c1), 
            notate(self.gold_spent, N).rjust(c2))
        print(hline)
        print('\t\u2020 Does not multiply with HoM or Bosses.')
        print('\t\u2021 Does not multiply with HoM.')

        if (self.pet_damage_per_attack and self.splash_damage):
            c1, c2, c3 = (13, 17, 20)
            hline = '\t'+'\u2015'*(c1+c2+c3+2)
            print('\n\n\t'+'SPLASH RESULTS BY STAGE (PET ATTACKS):')
            print(hline)
            print('\t'+'Splash Amount'.rjust(c1), 
                'Splash Maximum'.rjust(c2),
                'Splash Floor'.rjust(c3))
            print(hline)
            for i, splash_amount in enumerate(self.splash_amounts):
                print('\t'+('x'+str(splash_amount)).rjust(c1),
                    str(self.max_splash_stages[i]).rjust(c2),
                    str(self.min_splash_stages[i]).rjust(c3))
            print(hline)
            print('\tSplash Factor:', self.splash_damage)

        if self.evolve1_stage.max():
            hline = '\t'+'\u2015'*(54)
            print('\n\n\t'+'HERO EVOLVE STAGES:')
            print(hline)
            print('\t'+'1st Evolve: ', self.evolve1_stage[:8],
                '\n\t\t\t\t', self.evolve1_stage[8:16], 
                '\n\t\t\t\t', self.evolve1_stage[16:24], 
                '\n\t\t\t\t', self.evolve1_stage[24:32], 
                '\n\t\t\t\t', self.evolve1_stage[32:])
            print('\t'+'2nd Evolve: ', self.evolve2_stage[:8],
                '\n\t\t\t\t', self.evolve2_stage[8:16], 
                '\n\t\t\t\t', self.evolve2_stage[16:24], 
                '\n\t\t\t\t', self.evolve2_stage[24:32], 
                '\n\t\t\t\t', self.evolve2_stage[32:])

        c1, c2, c3, c4, c5 = (15, 10, 16, 16, 16)
        hline = '\t'+'\u2015'*(c1+c2+c3+c4+c5+4)
        print('\n\n\t'+'ATTACKS AND TIMES TO REACH STAGE:', self.stage)
        print(hline)
        print('\t'+'Attack Interval'.rjust(c1), 
            'Attacks'.rjust(c2),
            'Active Time'.rjust(c3),
            'Wasted Time'.rjust(c4),
            'Total Time'.rjust(c5))
        print(hline)
        for i, duration in enumerate(self.attack_durations):
            print('\t'+(str(duration)+' sec').rjust(c1),
                notate(self.general_performance[i, 0], N).rjust(c2),
                convert_time(self.general_performance[i, 1]).rjust(c3),
                convert_time(self.general_performance[i, 2]).rjust(c4),
                convert_time(self.general_performance[i, 1:].sum()).rjust(c5))
        print(hline)  
        if self.tap_performance[0]:
            print('\t'+'Tap Attacks'.ljust(c1),
                notate(self.tap_performance[0], N).rjust(c2),
                convert_time(self.tap_performance[1].sum()).rjust(c3),
                convert_time(self.tap_performance[2].sum()).rjust(c4),
                convert_time(self.tap_performance[1:].sum()).rjust(c5))
        if self.hs_performance[0]:  
            print('\t'+'Heav. Strikes'.ljust(c1),
                notate(self.hs_performance[0], N).rjust(c2),
                convert_time(self.hs_performance[1]).rjust(c3),
                convert_time(self.hs_performance[2]).rjust(c4),
                convert_time(self.hs_performance[1:].sum()).rjust(c5))
        if self.pet_performance[0]:
            print('\t'+'Pet Attacks'.ljust(c1), 
                notate(self.pet_performance[0], N).rjust(c2),
                convert_time(self.pet_performance[1]).rjust(c3),
                convert_time(self.pet_performance[2]).rjust(c4),
                convert_time(self.pet_performance[1:].sum()).rjust(c5))
        print(hline)  
        print('\tKillAnimationTime + DeviceLag + MeasurementLag:', 
            SVM.killAnimationTime+self.device_lag+self.measurement_delay, 'sec')


def run_simulation(input_csv, silent=False):

    # Store all input and game data into single object.
    data = GameData(input_csv)

    # Initialize player object.
    player = Player(data)

    # Max-stage simulation:
    while player.end_simulation is False:
        player.buy_sword_master(data.sword_master)
        player.buy_heroes(data.heroes)
        player.hero_improvement_bonuses(data)
        player.calc_dps(data.heroes)
        player.fight_titans(data.stage)
        player.fight_boss(data.stage)

    player.finalize_results(data)
    player.print_results(data.stage, silent)
    return (player, data.stage)


if __name__ == '__main__':
    player, stage = run_simulation('SwordMaster.csv')

    # Plotting.relic_efficiency(player, stage)
    # Plotting.mana_regen_per_stage(player, stage)
    # Plotting.time_per_stage(player, stage)
    # Plotting.dps_vs_bosshp(player, stage)
    # Plotting.dps_vs_gold(player, stage)
    # Plotting.tap_damage(player, stage)
    # Plotting.splash(player, stage, max_splash=20)