KING = "Craft_Upgrade_DamL2DurL2BalL2"

SOCKET_UPGRADES = [
    "Craft_Upgrade_Dam",
    "Craft_Upgrade_Dur",
    "Craft_Upgrade_Bal",
    "Craft_Upgrade_DamDur",
    "Craft_Upgrade_DamBal",
    "Craft_Upgrade_DurBal",
    "Craft_Upgrade_DamDurBal",
    "Craft_Upgrade_DamL2",
    "Craft_Upgrade_DurL2",
    "Craft_Upgrade_BalL2",
    "Craft_Upgrade_DamL2DurL2",
    "Craft_Upgrade_DamL2BalL2",
    "Craft_Upgrade_DurL2BalL2",
    "Craft_Upgrade_DamL2DurL2BalL2",
    "Craft_Upgrade_DamL2Dur",
    "Craft_Upgrade_DamL2Bal",
    "Craft_Upgrade_DurL2Bal",
    "Craft_Upgrade_DurL2Dam",
    "Craft_Upgrade_BalL2Dam",
    "Craft_Upgrade_BalL2Dur",
    "Craftplan_GTFO20",
    "Craftplan_LightingRod",
    "Throwable_PoisonGrenade",
    "Craftplan_GodHammer",
    "Craftplan_AngelSword",
    "Craftplan_AllInOne",
    "Craftplan_ToxicReaper"
]

def max_kings(item):
    item["upgradeSockets"] = [KING] * 4


def max_quantity(item):
    if "quantity" in item:
        item["quantity"] = 999999999


def max_skill(item):
    if "stacks" in item:
        item["stacks"] = 9999
    elif "unknown" in item and "unknown001" in item["unknown"]:
        item["unknown"]["unknown001"] = 9999
        
def set_rarity(item, rarity):
    if not isinstance(item, dict):
        return

    if "attributes" not in item:
        item["attributes"] = {}

    item["attributes"]["color"] = rarity


def set_platinum(item):
    set_rarity(item, "platinum")
    
def get_duplicate_id_map(items):
    id_map = {}

    for item in items:
        item_id = item.get("id")
        if not item_id:
            continue

        id_map.setdefault(item_id, []).append(item)

    return {k: v for k, v in id_map.items() if len(v) > 1}
    
LEGEND_SKILLS = [
    "LegendSkill_UnarmedDamage",
    "LegendSkill_OneHandedDamage",
    "LegendSkill_TwoHandedDamage",
    "LegendSkill_FirearmsDamage",
    "LegendSkill_BowDamage",
    "LegendSkill_ThrowingDamage",
    "LegendSkill_MaxStamina",
    "LegendSkill_MaxHealth",
    "LegendSkill_HealthRegeneration",
    "LegendSkill_HealingEfficiency"
]

ORANGE_CRAFTPLANS = [
    "Craftplan_GodHammer",
    "Craftplan_AngelSword",
    "Craftplan_AllInOne",
    "Craftplan_LightingRod",
    "Craftplan_ToxicReaper"
]

WEAPON_NAMES = [
    "ZZZZZ_MacheteBKorek2",
    "MacheteAKorek",
    "DevCraftExcalibour",
    "DevCraftAirStrike",
    "DevRightHandofgloVA",
    "DevCraftSiCKBomb"
]

COLLECTIBLES = [
    "ZZZZ_Collectable_CollectableOutfit_01",
    "ZZZZ_Collectable_CollectableOutfit_02",
    "ZZZZ_Collectable_CollectableOutfit_03",
    "ZZZZ_Collectable_CollectableOutfit_04",
    "ZZZZ_Collectable_CollectableOutfit_05",
    "ZZZZ_Collectable_CollectableOutfit_06",
    "ZZZZ_Collectable_CollectableOutfit_07",
    "ZZZZ_Collectable_CollectableOutfit_08",
    "ZZZZ_Collectable_CollectableOutfit_09",
    "ZZZZ_Collectable_CollectableOutfit_10",
    "ZZZZ_Collectable_CollectableOutfit_11",
    "ZZZZ_Collectable_CollectableOutfit_12"
]