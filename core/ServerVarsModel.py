class SVM(object):
     """
     Exported directly from the APK, with minor syntax changes
     to suit Python, and a few removals of variables that weren't needed.
     """

     serverVarsVersion = "default"

     minVersion = "1.0.4"

     maxGold = 1E+260

     chestersonChance = 0.01

     manaMonsterChance = 0.005

     goldx10Chance = 0.005

     chanceForManaSteal = 0.005

     manaRegenBaseInMinutes = 2

     interstitialChance = 0.02

     monsterCountBase = 10

     monsterCountInc = 4

     maxMonsterCount = 30

     maxStage = 3500

     inactiveGoldButtonCount = 1

     inactiveGoldButtonVideoCount = 50

     inactiveGoldMinSyncDays = 3

     inactiveGoldMonsterCap = 30000

     maxSplashSkillCount = 3

     petMidasUseBaseGold = True

     midasUseBaseGold = False

     midasMultiplierNormal = 1.0

     midasMultiplierChesterson = 30.0

     midasMultiplierBoss = 500.0

     maxDateOffset = 1

     tapsPerSecond = 20

     tapCoolDown = 0.01

     tapDamageCap = 3.0 #?

     tapDamageCapLevel = 500.0 #?

     playerUpgradeCostBase = 5

     playerUpgradeCostGrowth = 1.062

     playerCritChance = 0.002

     playerSuperCritChance = 0.002 #?

     maxCritChance = 0.5

     playerCritMinMult = 3

     playerCritMaxMult = 20

     playerAutoImprovementLevel = 25

     playerAutoImprovementAmount = 2

     multiMonsterBaseChance = 0.01

     skillPointsStageMin = 51

     skillPointsStageDelta = 500

     skillPointsPrestigeMin = 50

     skillPointsPrestigeDelta = 50

     manaCapInitial = 0

     manaCapPerSkill = 35

     swipeAttackSpeed = 3

     critSkillLightningAmount = 0.05

     midasSkillCoinMult = 0.5

     helperSkillFireChance = 0.05

     killAnimationTime = 0.3

     offlineKillAnimationTime = 0.7 #updated

     activeSkillCostMult = 12.0

     prestigeLevelReq = 600

     petDamageIncLevel1 = 40

     petDamageIncLevel2 = 80

     maxShadowCloneAniPerSec = 4.0

     petCageHPMultiplier = 15.0

     clanMakeItRainPercent = 0.2

     localDiamondRewardBase = 50

     localDiamondRewardInc = 5

     petTapAmount = 20

     petAutoAttackLevel = 500

     petAutoAttackInactiveLevel = 100

     bossQTEFinalBlowMultiplier = 10.0

     maxPetSpeedBoost = 10.0

     petAutoAttackDuration = 3

     minBossQTEAmount = 2

     maxBossQTEAmount = 5

     hoursToCollectEgg = 4

     petPassiveLevelGap = 5

     petPassiveLevelIncrement = 0.01

     maximumSalvageCost = 5000

     artifactUpgradeServerTime = 2

     maxLockableSlots = 10

     maxEquipmentSlots = 40

     equipmentStageMin = 56

     equipmentStageDelta = 20

     transmorphStageRequirement = 2000

     equipmentRareToCommonModifier = 3

     equipmentLegendaryToCommonModifier = 10

     minFarmingStage = 200

     clanDungoenPlayTime = 30

     clanDungoenBetweenFreePlayTime = 60

     clanDungoenHeroTaps = 3

     fairyFatChance = 0.05

     fairyAdChance = 0.2

     fairyAdChanceFirstTime = 0.4

     fairyAdFirstSessionExpireTimeMin = 40

     fairyCoinChestersonCount = 2

     fairyVideoDiamondCount = 5

     twitterFollowDiamonds = 25

     facebookLikeDiamonds = 25

     fairyStartStage = 10

     videoFairyStartStage = 50

     fatFairyRewardTime = 1440

     adsManaRefillChance = 0.07

     adsDiamondsChance = 0.31

     adsHandMidasChance = 0.31

     adsManaRefillPercentRequired = 0.7

     fairyDropCoinsChance = 0.5

     makeItRainChestersonCount = 200

     clanMakeItRainChestersonCount = 300

     makeItRainFairyCount = 15

     clanMakeItRainChestCount = 4

     numberOfClanCratesOnStage = 3

     goldenEggDiamondCost = 500

     currentDialogueIndex = 0

     currentDialogueCap = 100

     shopCurrentlyActive = True

     shopDaysTilNextDialogue = 2

     promptStage = 100

     promptTimes = 3

     createClanCost = 200

     clanMaxMessageStorage = 100

     clanShipDmgMult = 0.2

     clanShipAttackRate = 10 #This is duration, not rate.

     clanMaxMembers = 50

     helperUpgradeBase = 1.082

     helperInefficiency = 0.023

     dMGScaleDown = 0.1

     helperInefficiencySlowDown = 34

     initialPlayerCostOffset = 3

     tapCostSlowDownLevel = 25

     helperEvolveLevel1 = 999

     helperEvolveLevel2 = 1999

     helperQTEDuration = 15

     evolveCostMultiplier = 1000

     passiveSkillCostMultiplier = 10

     playerDamageMult = 1

     skillCostMultiplier = 3

     relicFromStageBaseline = 75

     relicFromStageDivider = 14

     relicFromStagePower = 1.75

     relicFromStageMult = 1

     relicFromHelperLevel = 1000

     relicBossDropChance = 0.3

     artifactSalvageLogBase = 8

     artifactSalvagePowerBase = 3.2

     artifactCostBase = 1.31

     minimumSalvageCost = 43

     artifactSalvageCostBaseScale = 10

     monsterHPBase1 = 1.39

     monsterHPBase2 = 1.13

     monsterHPMultiplier = 17.5

     monsterGoldMultiplier = 0.008

     monsterGoldSlope = 0.0002

     treasureGold = 10

     offlineCapInSeconds = 86400

     treasureBoxChance = 0.02

     monsterHPLevelOff = 115

     bossGoldMultiplier = 2

     noMoreMonsterGoldSlope = 150

     maxBossGoldMultiplier = 3

     bossGoldMultiplierSlope = 0.2

     themeMultiplierSequence = [2, 3, 4, 5, 8]

     bossHPModBase = 1.1

     skillResetMultiplier = 20

     manaMonsterPercentage = 0.5

     maxMemoryAmount = 0.5

     clanBonusBase = 1.1

     clanBonusBaseNerf = 1.05

     clanMemoryBase = 0.001

     clanMemoryBaseNerf = 0.0005

     clanQuestStageNerf = 200

     startingGoldMonsterCount = 20

     maxhelperAttackSpeedPerSec = 6

     doomMultiplier = 100.0

     minScientific = 1E+15

     tournamentBonusHelper = 2.0

     tournamentBonusMeleeHelper = 3.0

     tournamentBonusRangeHelper = 3.0

     tournamentBonusSpellHelper = 3.0

     tournamentBonusTapDamage = 2.0

     tournamentBonusManaRegen = 1.0

     tournamentBonusManaPool = 50.0

     tournamentBonusDoubleFairy = 0.4

     tournamentBonusCritChance = 0.1

     tournamentOfflineStageCap = 15

     tournamentForceUpdateScore = 10

     tournamentUpdateCooldown = 180.0

     maxHelperFormula = 34