import json
import random

# Load unified item data
with open("item_data.json") as f:
    all_items = json.load(f)

item_lookup = {item["name"].lower(): item for item in all_items}
item_names = [item["name"] for item in all_items]

with open("manufacturing_boons.json") as f:
    boon_table = json.load(f)
with open("manufacturing_flaws.json") as f:
    flaw_table = json.load(f)

def roll_d20(adv):
    r1, r2 = random.randint(1, 20), random.randint(1, 20)
    return max(r1, r2) if adv == "adv" else min(r1, r2) if adv == "dis" else r1

def get_quirk_count(diff):
    if diff <= -13: return {"flaws": "destroyed", "boons": 0}
    elif -12 <= diff <= -9: return {"flaws": 3, "boons": 0}
    elif -8 <= diff <= -5: return {"flaws": 2, "boons": 0}
    elif -4 <= diff <= -1: return {"flaws": 1, "boons": 0}
    elif 0 <= diff <= 4: return {"flaws": 0, "boons": 0}
    elif 5 <= diff <= 8: return {"flaws": 0, "boons": 1}
    elif 9 <= diff <= 12: return {"flaws": 0, "boons": 2}
    else: return {"flaws": 0, "boons": 3}

def roll_boon(restricted, existing_boons):
    while True:
        roll = random.randint(1, 20)
        for b in boon_table:
            if b["range"][0] <= roll <= b["range"][1]:
                if b["name"] in existing_boons:
                    break
                if b.get("excluded_types") and any(t in restricted for t in b["excluded_types"]):
                    break
                if b["reroll_if_invalid"] and not any(t in restricted for t in b["restricted_types"]):
                    break
                return b

def roll_flaw(restricted, existing_flaws):
    while True:
        roll = random.randint(1, 20)
        for f in flaw_table:
            if f["range"][0] <= roll <= f["range"][1]:
                if f["name"] in existing_flaws:
                    break
                if f["name"].startswith("Poor") and not any(t in restricted for t in f["restricted_types"]):
                    return next(x for x in flaw_table if x["name"] == "Fragile")
                return f

def perform_crafting_check(item_name, bonus, adv, magic):
    item = item_lookup.get(item_name.lower())
    if not item:
        return f"❌ Item '{item_name}' not found."

    tool_match = "Smith" in item.get("tool_required", [])
    adjusted_adv = adv
    if magic == "Forgekeeper's Spark" and tool_match:
        if adv == "none":
            adjusted_adv = "adv"
        elif adv == "dis":
            adjusted_adv = "none"

    roll = roll_d20(adjusted_adv)
    total = roll + bonus
    diff = total - item["dc"]
    quirks = get_quirk_count(diff)
    out = ""

    if quirks["flaws"] == "destroyed":
        return f"❌ Your check result was too low. The item is destroyed during crafting."

    boons = []
    flaws = []
    for _ in range(quirks["boons"]):
        b = roll_boon(item["restricted_types"], [boon["name"] for boon in boons])
        if b: boons.append(b)
    for _ in range(quirks["flaws"]):
        f = roll_flaw(item["restricted_types"], [flaw["name"] for flaw in flaws])
        if f: flaws.append(f)

    base = item["item_value_gp"]
    mult = 1 + 0.1 * len(boons) - 0.1 * len(flaws)
    if any(b["name"] == "Magnificent Finish" for b in boons): mult *= 2
    if any(f["name"] == "Mediocre Finish" for f in flaws): mult *= 0.5

    final_val = round(base * mult)
    restricted_types = item.get("restricted_types", [])
    time_hours = item['time_hours']

    if magic == "Forgekeeper's Spark" and tool_match and roll >= 15:
        time_hours = round(time_hours / 2, 2)

    if "armor" in restricted_types:
        item_output = f"{item['name']}" if item.get("type") == "shield" else f"{item['name']} {item.get('type')}"
        out = f"You spent {time_hours} hours and {item['material_cost_gp']} gp crafting a {item_output}, valued at {final_val} gp with "
    elif "weapon" in restricted_types:
        readable_type = item.get("type", "weapon")
        out = f"You spent {time_hours} hours and {item['material_cost_gp']} gp crafting a {item['name']}, a {readable_type} valued at {final_val} gp with "
    else:
        out = f"You spent {time_hours} hours and {item['material_cost_gp']} gp crafting a {item['name']}, valued at {final_val} gp with "

    if boons:
        out += f"{len(boons)} boon{'s' if len(boons) > 1 else ''}: {', '.join(b['name'] for b in boons)}. \n"
    elif flaws:
        out += f"{len(flaws)} flaw{'s' if len(flaws) > 1 else ''}: {', '.join(f['name'] for f in flaws)}. \n"
    else:
        out += "no quirks. \n"
    
    out += (f"`With a D20test of {roll} and a bonus of {bonus}, the total check is {total}.`")
    return out




