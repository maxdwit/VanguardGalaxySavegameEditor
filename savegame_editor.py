#!/usr/bin/env python3
import gzip
import json
import sys
import os
from pathlib import Path


FACTION_NAMES = {
    'MiningGuild': 'Mindus Holdings',
    'PoliceGuild': 'Canisec',
    'BountyGuild': 'Orsanon Security',
    'SalvageGuild': 'Steel Vultures',
    'TradingGuild': 'Intertrade Network',
    'IndustrialGuild': 'Forge Industries',
    'Marauders': 'Corsair Syndicate',
    'Smugglers': 'Void Drifters',
    'Blue': 'Stellar Industries',
    'Red': 'Kolyatov Collective',
    'Gold': 'Luminate Combine',
    'Darkspacers': 'Darkspace Compact',
    'Fanatics': "Meridia's Chosen",
    'Puppeteers': 'Umbral Reach',
    'Player': 'Player',
    'Stranded': 'Stranded',
    'Amalgam': 'Amalgam',
    'HolyRadicals': 'Holy Radicals'
}

ORE_CRYSTAL_NAMES = {
    'OreCommon1': 'Cerrax',
    'OreCommon10': 'Onexel',
    'OreCommon20': 'Baryth',
    'OreCommon30': 'Orminite',
    'OreCommon40': 'Argenthyte',
    'OreCommon50': 'Zorinite',
    'OreCommon60': 'Lithar',
    'OreCommon70': 'Torvenite',
    'OreCommon80': 'Crysaline',
    'OreCommon90': 'Thalorene',
    'OreCommon100': 'Lunorite',
    'OreCommon7': 'Dense Cerrax',
    'OreCommon16': 'Dense Onexel',
    'OreCommon26': 'Dense Baryth',
    'OreCommon36': 'Dense Orminite',
    'OreCommon46': 'Dense Argenthyte',
    'OreCommon56': 'Dense Zorinite',
    'OreCommon66': 'Dense Lithar',
    'OreCommon76': 'Dense Torvenite',
    'OreCommon86': 'Dense Crysaline',
    'OreCommon96': 'Dense Thalorene',
    'OreCommon106': 'Dense Lunorite',
    'OreCommon13': 'Rich Cerrax',
    'OreCommon22': 'Rich Onexel',
    'OreCommon32': 'Rich Baryth',
    'OreCommon42': 'Rich Orminite',
    'OreCommon52': 'Rich Argenthyte',
    'OreCommon62': 'Rich Zorinite',
    'OreCommon72': 'Rich Lithar',
    'OreCommon82': 'Rich Torvenite',
    'OreCommon92': 'Rich Crysaline',
    'OreCommon102': 'Rich Thalorene',
    'OreCommon112': 'Rich Lunorite',
    'OreRare1': 'Amberic',
    'OreRare10': 'Dromium',
    'OreRare20': 'Halcyonite',
    'OreRare30': 'Neonine',
    'OreRare40': 'Tachyline',
    'OreRare50': 'Xenorite',
    'OreRare60': 'Caldras',
    'OreRare70': 'Drakitium',
    'OreRare80': 'Xylenite',
    'OreRare90': 'Erythrite',
    'OreRare100': 'Omegane',
    'OreRare7': 'Pure Amberic',
    'OreRare16': 'Pure Dromium',
    'OreRare26': 'Pure Halcyonite',
    'OreRare36': 'Pure Neonine',
    'OreRare46': 'Pure Tachyline',
    'OreRare56': 'Pure Xenorite',
    'OreRare66': 'Pure Caldras',
    'OreRare76': 'Pure Drakitium',
    'OreRare86': 'Pure Xylenite',
    'OreRare96': 'Pure Erythrite',
    'OreRare106': 'Pure Omegane',
    'OreRare13': 'Radiant Amberic',
    'OreRare22': 'Radiant Dromium',
    'OreRare32': 'Radiant Halcyonite',
    'OreRare42': 'Radiant Neonine',
    'OreRare52': 'Radiant Tachyline',
    'OreRare62': 'Radiant Xenorite',
    'OreRare72': 'Radiant Caldras',
    'OreRare82': 'Radiant Drakitium',
    'OreRare92': 'Radiant Xylenite',
    'OreRare102': 'Radiant Erythrite',
    'OreRare112': 'Radiant Omegane',
    'OreUncommon106': 'Dense Promethium',
    'OreUncommon112': 'Rich Promethium',
    'ColdCrystal': 'Cryonos Crystal',
    'CorrosionCrystal': 'Viracid Crystal',
    'EnergyCrystal': 'Pulseite Crystal',
    'ExplosiveCrystal': 'Pyroc Crystal',
    'HeatCrystal': 'Meltrax Crystal',
    'KineticCrystal': 'Kinetos Crystal',
    'RadiationCrystal': 'Ravenoryx Crystal',
    'BallisticCrystal': 'Ares Core',
    'ModuleCrystal': 'Athena Prism'
}


def load_savegame(filename):
    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        return json.load(f)


def get_player_credits(data):
    credits = data.get('Player', {}).get('credits', '0')
    return int(credits) if isinstance(credits, str) else credits


def set_player_credits(data, amount):
    data['Player']['credits'] = str(amount)


def get_reputation_tier(reputation):
    if reputation >= 15000:
        return "Respected", 15000
    elif reputation >= 10000:
        return "Friendly", 10000
    elif reputation >= 3500:
        return "Cordial", 3500
    elif reputation >= 1500:
        return "Neutral", 1500
    elif reputation >= -1000:
        return "Unfriendly", -1000
    else:
        return "Despised", -15000


def get_current_poi_material_storage(data):
    current_poi = data.get('Player', {}).get('currentPointOfInterest', '')
    if not current_poi:
        return None
    
    map_data = data.get('Player', {}).get('map', {})
    sectors = map_data.get('sectors', [])
    
    for sector in sectors:
        for system in sector.get('systems', []):
            for poi in system.get('pointsOfInterest', []):
                if poi.get('guid') == current_poi:
                    return poi.get('materialStorage', {})
    return None


def get_material_storage(data):
    storage = get_current_poi_material_storage(data)
    if not storage:
        return []
    
    materials = []
    for item in storage.get('items', []):
        item_id = item.get('item', '')
        count = item.get('count', 0)
        display_name = ORE_CRYSTAL_NAMES.get(item_id, item_id)
        materials.append({
            'item_id': item_id,
            'name': display_name,
            'count': count,
            'item_ref': item
        })
    return materials


def get_all_stations_with_materials(data):
    map_data = data.get('Player', {}).get('map', {})
    sectors = map_data.get('sectors', [])
    stations = []
    
    for sector in sectors:
        zone_name = sector.get('name', 'Unknown Zone')
        for system in sector.get('systems', []):
            system_name = system.get('name', 'Unknown System')
            
            for poi in system.get('pointsOfInterest', []):
                poi_name = poi.get('name', 'Unknown')
                poi_guid = poi.get('guid', '')
                material_storage = poi.get('materialStorage', {})
                items = material_storage.get('items', [])
                
                if items:
                    stations.append({
                        'name': poi_name,
                        'guid': poi_guid,
                        'system': system_name,
                        'zone': zone_name,
                        'items': items,
                        'poi_ref': poi
                    })
    
    stations.sort(key=lambda s: (s['zone'], s['system'], s['name']))
    return stations


def set_material_amount(data, item_ref, amount):
    item_ref['count'] = int(amount)


def get_player_factions(data):
    faction_data = data.get('Player', {}).get('factionData', [])
    player_factions = []
    
    for entry in faction_data:
        faction_id = None
        
        if entry.get('f2') == 'Player':
            faction_id = entry.get('f1')
        elif entry.get('f1') == 'Player':
            faction_id = entry.get('f2')
        
        if faction_id:
            rep = entry.get('reputation', 0)
            tier_name, tier_min = get_reputation_tier(rep)
            faction_display_name = FACTION_NAMES.get(faction_id, faction_id)
            player_factions.append({
                'faction': faction_display_name,
                'faction_id': faction_id,
                'reputation': rep,
                'tier': tier_name,
                'tier_min': tier_min,
                'entry': entry
            })
    
    return player_factions


def edit_faction_reputation(faction_entry):
    current_rep = faction_entry.get('reputation', 0)
    faction_name = faction_entry.get('f1', 'Unknown')
    
    while True:
        new_value = input(f"Enter new reputation for {faction_name} (current: {current_rep}, range: -25000 to 15000): ").strip()
        if not new_value:
            return
        
        try:
            new_rep = int(new_value)
            if -25000 <= new_rep <= 15000:
                faction_entry['reputation'] = new_rep
                tier_name, _ = get_reputation_tier(new_rep)
                print(f"Updated {faction_name} to {new_rep:,} - {tier_name}")
                return
            else:
                print("Value must be between -25000 and 15000.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def edit_factions_menu(data, factions):
    while True:
        print("\nPlayer Faction Reputations:")
        for idx, faction in enumerate(factions):
            print(f"  {idx+1}. {faction['faction']}: {faction['reputation']:,} - {faction['tier']}")
        
        print(f"\n[1-{len(factions)}] Select faction to edit | [z/Z] Back")
        choice = input("Choice: ").strip().lower()
        
        if choice == 'z':
            break
        
        try:
            faction_idx = int(choice) - 1
            if 0 <= faction_idx < len(factions):
                edit_faction_reputation(factions[faction_idx]['entry'])
                factions = get_player_factions(data)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


def list_save_files(directory='.'):
    save_files = []
    for file in Path(directory).glob('*.save'):
        if file.is_file():
            mtime = file.stat().st_mtime
            save_files.append({'path': file, 'name': file.name, 'mtime': mtime})
    save_files.sort(key=lambda x: x['mtime'], reverse=True)
    return save_files


def select_save_file():
    save_files = list_save_files()
    
    if not save_files:
        print("No .save files found in current directory.")
        sys.exit(1)
    
    if len(save_files) == 1:
        print(f"Found 1 save file: {save_files[0]['name']}")
        return str(save_files[0]['path'])
    
    print("\nAvailable save files (newest first):")
    for idx, sf in enumerate(save_files):
        print(f"  {idx+1}. {sf['name']}")
    
    while True:
        choice = input(f"\nSelect save file [1-{len(save_files)}] (default: 1): ").strip()
        if not choice:
            return str(save_files[0]['path'])
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(save_files):
                return str(save_files[idx]['path'])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


def save_savegame(filename, data):
    with gzip.open(filename, 'wt', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))


def find_silverheart_items(data):
    silverheart_items = []
    ships = data['Player'].get('spaceShips', [])
    for i, ship in enumerate(ships):
        eq = ship.get('equipment', {})
        for slot, item in eq.items():
            if item and isinstance(item, dict) and 'Silverheart' in item.get('displayName', ''):
                silverheart_items.append({
                    'location': f'Ship {i} ({ship.get("type", "Unknown")})',
                    'slot': f'Equipment: {slot}',
                    'name': item.get('displayName'),
                    'ship_idx': i,
                    'slot_name': slot,
                    'item': item
                })
        
        hardpoints = ship.get('hardpoints', [])
        for hp_idx, item in enumerate(hardpoints):
            if item and isinstance(item, dict) and 'Silverheart' in item.get('displayName', ''):
                silverheart_items.append({
                    'location': f'Ship {i} ({ship.get("type", "Unknown")})',
                    'slot': f'Hardpoint {hp_idx}',
                    'name': item.get('displayName'),
                    'ship_idx': i,
                    'hp_idx': hp_idx,
                    'item': item
                })
    
    global_inv = data['Player'].get('globalInventory', [])
    for i, item in enumerate(global_inv):
        if item and isinstance(item, dict) and 'Silverheart' in item.get('displayName', ''):
            silverheart_items.append({
                'location': 'Global Inventory',
                'slot': f'Index {i}',
                'name': item.get('displayName'),
                'inv_idx': i,
                'item': item
            })
    
    return silverheart_items


def edit_item_stats(item):
    stats = item.get('stats', [])
    if not stats:
        print("No stats found for this item.")
        return
    
    while True:
        print("\nItem Stats:")
        for idx, stat in enumerate(stats):
            if 'multiplier' in stat:
                value = stat['multiplier']
                print(f"  {idx+1}. {stat.get('stat', 'Unknown')}: {value:.2f} (multiplier, {value*100:.1f}%)")
            else:
                value = stat.get('amount', stat.get('value', 0))
                print(f"  {idx+1}. {stat.get('stat', 'Unknown')}: {value:.2f}")
        
        print("\n[1-{}] Select stat to edit | [z/Z] Back".format(len(stats)))
        choice = input("Choice: ").strip().lower()
        
        if choice == 'z':
            break
        
        try:
            stat_idx = int(choice) - 1
            if 0 <= stat_idx < len(stats):
                stat = stats[stat_idx]
                if 'multiplier' in stat:
                    value_key = 'multiplier'
                elif 'amount' in stat:
                    value_key = 'amount'
                else:
                    value_key = 'value'
                
                current_value = stat.get(value_key, 0)
                stat_name = stat.get('stat', 'Unknown')
                
                if value_key == 'multiplier':
                    new_value = input(f"Enter new multiplier for {stat_name} (current: {current_value:.2f} = {current_value*100:.1f}%): ").strip()
                else:
                    new_value = input(f"Enter new value for {stat_name} (current: {current_value:.2f}): ").strip()
                
                if new_value:
                    stat[value_key] = float(new_value)
                    if value_key == 'multiplier':
                        print(f"Updated {stat_name} to {stat[value_key]:.2f} ({stat[value_key]*100:.1f}%)")
                    else:
                        print(f"Updated {stat_name} to {stat[value_key]:.2f}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


def find_active_ship_items(data):
    current_guid = data.get('Player', {}).get('currentSpaceShip', '')
    if not current_guid:
        return None, []
    
    ships = data['Player'].get('spaceShips', [])
    active_ship = None
    ship_idx = None
    
    for i, ship in enumerate(ships):
        if ship.get('guid') == current_guid:
            active_ship = ship
            ship_idx = i
            break
    
    if not active_ship:
        return None, []
    
    items = []
    ship_name = active_ship.get('customName', 'Active Ship')
    eq = active_ship.get('equipment', {})
    for slot, item in eq.items():
        if item and isinstance(item, dict):
            items.append({
                'location': f'Ship {ship_idx} ({ship_name})',
                'slot': f'Equipment: {slot}',
                'name': item.get('displayName', 'Unknown'),
                'ship_idx': ship_idx,
                'slot_name': slot,
                'item': item
            })
    
    hardpoints = active_ship.get('hardpoints', [])
    for hp_idx, item in enumerate(hardpoints):
        if item and isinstance(item, dict):
            items.append({
                'location': f'Ship {ship_idx} ({ship_name})',
                'slot': f'Hardpoint {hp_idx}',
                'name': item.get('displayName', 'Unknown'),
                'ship_idx': ship_idx,
                'hp_idx': hp_idx,
                'item': item
            })
    
    return active_ship, items


def get_item_aspects(item):
    if not isinstance(item, dict):
        return []
    
    aspect_slots = item.get('aspectSlots', [])
    aspects = []
    
    for slot in aspect_slots:
        if isinstance(slot, dict):
            aspect = slot.get('equipAspect')
            if aspect and aspect != 'None':
                aspects.append(aspect)
    
    return aspects


def get_active_ship_cargo(data):
    current_guid = data.get('Player', {}).get('currentSpaceShip', '')
    if not current_guid:
        return None, []
    
    ships = data['Player'].get('spaceShips', [])
    active_ship = None
    
    for ship in ships:
        if ship.get('guid') == current_guid:
            active_ship = ship
            break
    
    if not active_ship:
        return None, []
    
    cargo_items = []
    cargo_data = active_ship.get('cargo', {})
    cargo_list = cargo_data.get('items', [])
    
    for idx, cargo_entry in enumerate(cargo_list):
        if cargo_entry and isinstance(cargo_entry, dict):
            item = cargo_entry.get('item')
            count = cargo_entry.get('count', 1)
            
            if isinstance(item, dict):
                name = item.get('displayName', 'Unknown')
                aspects = get_item_aspects(item)
                
                if aspects:
                    aspect_str = ', '.join(aspects)
                    display_name = f"{name} (x{count}) [{aspect_str}]"
                else:
                    display_name = f"{name} (x{count})"
                
                cargo_items.append({
                    'name': display_name,
                    'cargo_idx': idx,
                    'item': item
                })
            elif isinstance(item, str):
                cargo_items.append({
                    'name': f"{item} (x{count})",
                    'cargo_idx': idx,
                    'item': cargo_entry,
                    'is_simple': True
                })
    
    return active_ship, cargo_items


def edit_active_ship_menu(data):
    while True:
        active_ship, items = find_active_ship_items(data)
        
        if active_ship is None:
            print("\nActive ship not found in savegame.")
            input("Press Enter to continue...")
            return
        
        if not items:
            print("\nNo items found on active ship.")
            input("Press Enter to continue...")
            return
        
        ship_name = active_ship.get('customName', 'Active Ship')
        print(f"\n{ship_name} Items:")
        for idx, item_info in enumerate(items):
            print(f"  {idx+1}. {item_info['name']} - {item_info['slot']}")
        
        print("\n[1-{}] Select item to edit | [z/Z] Back".format(len(items)))
        choice = input("Choice: ").strip().lower()
        
        if choice == 'z':
            break
        
        try:
            item_idx = int(choice) - 1
            if 0 <= item_idx < len(items):
                selected = items[item_idx]
                edit_item_stats(selected['item'])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


def get_armory_aspects(data):
    armory_data = data.get('Player', {}).get('globalInventory', {})
    armory_items = armory_data.get('items', [])
    
    aspects = []
    for idx, entry in enumerate(armory_items):
        if entry and isinstance(entry, dict):
            item = entry.get('item')
            if isinstance(item, dict) and item.get('itemType') == 'Aspect':
                aspect_name = item.get('aspectName', 'Unknown')
                display_name = item.get('displayName', 'Unknown')
                count = entry.get('count', 1)
                aspects.append({
                    'aspect_name': aspect_name,
                    'display_name': display_name,
                    'count': count,
                    'armory_idx': idx
                })
    
    return aspects


def duplicate_aspect_menu(data):
    _, cargo_items = get_active_ship_cargo(data)
    armory_aspects = get_armory_aspects(data)
    
    if not cargo_items and not armory_aspects:
        print("\nNo cargo items or armory aspects found.")
        input("Press Enter to continue...")
        return
    
    editable_items = [item for item in cargo_items if not item.get('is_simple', False)]
    
    if not editable_items and not armory_aspects:
        print("\nNo items with aspects found.")
        input("Press Enter to continue...")
        return
    
    print("\n=== Duplicate Aspect ===")
    
    all_sources = []
    
    if editable_items:
        print("\n--- Cargo Items ---")
        for idx, item_info in enumerate(editable_items):
            aspects = get_item_aspects(item_info['item'])
            aspect_str = ', '.join(aspects) if aspects else 'No aspects'
            print(f"  {len(all_sources)+1}. {item_info['item'].get('displayName', 'Unknown')} [{aspect_str}]")
            all_sources.append({'type': 'cargo', 'data': item_info, 'idx': idx})
    
    if armory_aspects:
        print("\n--- Armory Aspects ---")
        for aspect_info in armory_aspects:
            print(f"  {len(all_sources)+1}. {aspect_info['display_name']} (x{aspect_info['count']}) [{aspect_info['aspect_name']}]")
            all_sources.append({'type': 'armory', 'data': aspect_info})
    
    source_choice = input("\nSelect SOURCE (number): ").strip()
    if not source_choice:
        return
    
    try:
        source_idx = int(source_choice) - 1
        if not (0 <= source_idx < len(all_sources)):
            print("Invalid selection.")
            input("Press Enter to continue...")
            return
    except ValueError:
        print("Invalid input.")
        input("Press Enter to continue...")
        return
    
    source = all_sources[source_idx]
    
    if source['type'] == 'cargo':
        source_item = source['data']['item']
        source_aspects = get_item_aspects(source_item)
        
        if not source_aspects:
            print("\nSource item has no aspects to copy.")
            input("Press Enter to continue...")
            return
        
        print(f"\nSource aspects: {', '.join(source_aspects)}")
        
        if len(source_aspects) > 1:
            print("\nWhich aspect to copy?")
            for idx, asp in enumerate(source_aspects):
                print(f"  {idx+1}. {asp}")
            aspect_choice = input("Select aspect (number): ").strip()
            try:
                aspect_idx = int(aspect_choice) - 1
                if not (0 <= aspect_idx < len(source_aspects)):
                    print("Invalid selection.")
                    input("Press Enter to continue...")
                    return
                selected_aspect = source_aspects[aspect_idx]
            except ValueError:
                print("Invalid input.")
                input("Press Enter to continue...")
                return
        else:
            selected_aspect = source_aspects[0]
    else:
        selected_aspect = source['data']['aspect_name']
        print(f"\nSelected aspect: {selected_aspect}")
    
    print(f"\nCopying aspect: {selected_aspect}")
    
    if source['type'] == 'cargo':
        target_items = [item for i, item in enumerate(editable_items) if i != source['idx']]
    else:
        target_items = editable_items
    
    if not target_items:
        print("\nNo other items available as target.")
        input("Press Enter to continue...")
        return
    
    print("\nAvailable TARGET Items:")
    for idx, item_info in enumerate(target_items):
        aspects = get_item_aspects(item_info['item'])
        aspect_str = ', '.join(aspects) if aspects else 'No aspects'
        print(f"  {idx+1}. {item_info['item'].get('displayName', 'Unknown')} [{aspect_str}]")
    
    target_choice = input("\nSelect TARGET item (number): ").strip()
    if not target_choice:
        return
    
    try:
        target_idx = int(target_choice) - 1
        if not (0 <= target_idx < len(target_items)):
            print("Invalid selection.")
            input("Press Enter to continue...")
            return
    except ValueError:
        print("Invalid input.")
        input("Press Enter to continue...")
        return
    
    target_item = target_items[target_idx]['item']
    target_aspects = get_item_aspects(target_item)
    aspect_slots = target_item.get('aspectSlots', [])
    
    if len(target_aspects) >= 2:
        print(f"\nTarget already has 2 aspects: {', '.join(target_aspects)}")
        print("Which aspect to overwrite?")
        for idx, asp in enumerate(target_aspects):
            print(f"  {idx+1}. {asp}")
        overwrite_choice = input("Select aspect to overwrite (number): ").strip()
        try:
            overwrite_idx = int(overwrite_choice) - 1
            if not (0 <= overwrite_idx < len(target_aspects)):
                print("Invalid selection.")
                input("Press Enter to continue...")
                return
            
            slot_idx = 0
            for i, slot in enumerate(aspect_slots):
                if isinstance(slot, dict) and slot.get('equipAspect') == target_aspects[overwrite_idx]:
                    slot_idx = i
                    break
            
            aspect_slots[slot_idx]['equipAspect'] = selected_aspect
            print(f"\nReplaced '{target_aspects[overwrite_idx]}' with '{selected_aspect}'")
        except ValueError:
            print("Invalid input.")
            input("Press Enter to continue...")
            return
    else:
        empty_slot = None
        for slot in aspect_slots:
            if isinstance(slot, dict) and (slot.get('equipAspect') is None or slot.get('equipAspect') == 'None'):
                empty_slot = slot
                break
        
        if empty_slot:
            empty_slot['equipAspect'] = selected_aspect
            print(f"\nAdded aspect '{selected_aspect}' to target item.")
        else:
            if len(aspect_slots) < 2:
                aspect_slots.append({'equipAspect': selected_aspect, 'index': str(len(aspect_slots))})
                print(f"\nAdded aspect '{selected_aspect}' to new slot.")
            else:
                print("\nError: Could not add aspect (no empty slots).")
    
    input("\nPress Enter to continue...")


def edit_silverheart_menu(data):
    while True:
        silverheart_items = find_silverheart_items(data)
        active_ship, ship_items = find_active_ship_items(data)
        _, cargo_items = get_active_ship_cargo(data)
        
        print("\nSilverheart Items:")
        for idx, si in enumerate(silverheart_items):
            print(f"  {idx+1}. {si['name']} - {si['location']}, {si['slot']}")
        
        all_items = list(silverheart_items)
        current_idx = len(all_items)
        
        if active_ship and ship_items:
            print("\n--- Active Ship Equipment ---")
            ship_name = active_ship.get('customName', 'Active Ship')
            for item_info in ship_items:
                all_items.append(item_info)
                print(f"  {current_idx+1}. {item_info['name']} - {item_info['slot']}")
                current_idx += 1
        
        if cargo_items:
            print("\n--- Active Ship Cargo ---")
            for cargo_info in cargo_items:
                all_items.append(cargo_info)
                print(f"  {current_idx+1}. {cargo_info['name']}")
                current_idx += 1
        
        print("\n[1-{}] Select item to edit | [d/D] Duplicate Aspect | [z/Z] Back".format(len(all_items)))
        choice = input("Choice: ").strip().lower()
        
        if choice == 'z':
            break
        elif choice == 'd':
            duplicate_aspect_menu(data)
            continue
        
        try:
            item_idx = int(choice) - 1
            if 0 <= item_idx < len(all_items):
                selected = all_items[item_idx]
                edit_item_stats(selected['item'])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


def list_all_stations_menu(data):
    stations = get_all_stations_with_materials(data)
    
    if not stations:
        print("\nNo stations with material storage found.")
        input("Press Enter to continue...")
        return
    
    print(f"\nStations with Material Storage ({len(stations)} found):")
    print("="*80)
    
    current_zone = None
    for idx, station in enumerate(stations):
        if station['zone'] != current_zone:
            current_zone = station['zone']
            print("\n" + "-"*80)
            print(f"ZONE: {current_zone}")
            #rint("-"*80)
        
        print(f"\n{idx+1}. {station['name']} ({station['system']})")
        print(f"   Items ({len(station['items'])}):")  
        
        for item in station['items']:
            if item and isinstance(item, dict):
                item_id = item.get('item', '')
                count = item.get('count', 0)
                display_name = ORE_CRYSTAL_NAMES.get(item_id, item_id)
                print(f"     - {display_name}: {count}")
    
    print("\n" + "="*80)
    input("\nPress Enter to continue...")


def edit_materials_menu(data):
    while True:
        materials = get_material_storage(data)
        
        if not materials:
            print("\nNo material storage found in current station.")
            input("Press Enter to continue...")
            return
        
        print("\nMaterial Storage (Ores & Crystals):")
        for idx, mat in enumerate(materials):
            print(f"  {idx+1}. {mat['name']}: {mat['count']}")
        
        print(f"\n[1-{len(materials)}] Select material to edit | [z/Z] Back")
        choice = input("Choice: ").strip().lower()
        
        if choice == 'z':
            break
        
        try:
            mat_idx = int(choice) - 1
            if 0 <= mat_idx < len(materials):
                mat = materials[mat_idx]
                while True:
                    new_value = input(f"Enter new amount for {mat['name']} (current: {mat['count']}, must be > 0): ").strip()
                    if not new_value:
                        break
                    
                    try:
                        new_amount = int(new_value)
                        if new_amount > 0:
                            set_material_amount(data, mat['item_ref'], new_amount)
                            print(f"Updated {mat['name']} to {new_amount}")
                            break
                        else:
                            print("Value must be greater than 0.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


def display_info(credits, factions):
    print(f"\nCredits: {credits:,}")
    print("\nPlayer Faction Reputations:")
    for faction in factions:
        print(f"  {faction['faction']}: {faction['reputation']:,} - {faction['tier']}")


def main():
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = select_save_file()
    
    data = load_savegame(filename)
    credits = get_player_credits(data)
    factions = get_player_factions(data)
    
    display_info(credits, factions)
    
    while True:
        choice = input("\n[+] Add 1M Credits | [e/E] Edit Items | [f/F] Edit Factions | [m/M] Material Storage | [!] List All Stations | [s/S] Save | [q/Q] Quit: ").strip()
        if choice == '+':
            credits += 1000000
            set_player_credits(data, credits)
            print(f"Credits increased to: {credits:,}")
        elif choice.lower() == 'e':
            edit_silverheart_menu(data)
            display_info(credits, factions)
        elif choice.lower() == 'f':
            edit_factions_menu(data, factions)
            factions = get_player_factions(data)
            display_info(credits, factions)
        elif choice.lower() == 'm':
            edit_materials_menu(data)
            display_info(credits, factions)
        elif choice == '!':
            list_all_stations_menu(data)
            display_info(credits, factions)
        elif choice.lower() == 's':
            output_filename = input("\nEnter save filename (default: CHEATX.save): ").strip()
            if not output_filename:
                output_filename = 'CHEATX.save'
            if not output_filename.endswith('.save'):
                output_filename += '.save'
            save_savegame(output_filename, data)
            print(f"Saved to {output_filename}")
            break
        elif choice.lower() == 'q':
            print("Exiting without saving.")
            break


if __name__ == '__main__':
    main()
