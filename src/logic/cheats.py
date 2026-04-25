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
    "Craft_Upgrade_BalL2Dur"
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