KING = "Craft_Upgrade_DamL2DurL2BalL2"

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