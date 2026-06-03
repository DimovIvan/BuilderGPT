import gzip
import re
import struct
from typing import Dict, Iterable, Tuple

Placement = Tuple[int, int, int, str]

TAG_END = 0
TAG_SHORT = 2
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10

WOOD_VARIANTS = {
    "oak": 0,
    "spruce": 1,
    "birch": 2,
    "jungle": 3,
    "acacia": 4,
    "dark_oak": 5,
    "mangrove": 0,
    "cherry": 0,
    "bamboo": 0,
    "crimson": 0,
    "warped": 0,
}

COLORS = {
    "white": 0,
    "orange": 1,
    "magenta": 2,
    "light_blue": 3,
    "yellow": 4,
    "lime": 5,
    "pink": 6,
    "gray": 7,
    "light_gray": 8,
    "cyan": 9,
    "purple": 10,
    "blue": 11,
    "brown": 12,
    "green": 13,
    "red": 14,
    "black": 15,
}

BASE_BLOCKS: Dict[str, Tuple[int, int]] = {
    "minecraft:air": (0, 0),
    "minecraft:stone": (1, 0),
    "minecraft:granite": (1, 1),
    "minecraft:polished_granite": (1, 2),
    "minecraft:diorite": (1, 3),
    "minecraft:polished_diorite": (1, 4),
    "minecraft:andesite": (1, 5),
    "minecraft:polished_andesite": (1, 6),
    "minecraft:grass": (2, 0),
    "minecraft:grass_block": (2, 0),
    "minecraft:dirt": (3, 0),
    "minecraft:coarse_dirt": (3, 1),
    "minecraft:podzol": (3, 2),
    "minecraft:cobblestone": (4, 0),
    "minecraft:bedrock": (7, 0),
    "minecraft:water": (9, 0),
    "minecraft:lava": (11, 0),
    "minecraft:sand": (12, 0),
    "minecraft:red_sand": (12, 1),
    "minecraft:gravel": (13, 0),
    "minecraft:gold_ore": (14, 0),
    "minecraft:iron_ore": (15, 0),
    "minecraft:coal_ore": (16, 0),
    "minecraft:glass": (20, 0),
    "minecraft:lapis_ore": (21, 0),
    "minecraft:lapis_block": (22, 0),
    "minecraft:dispenser": (23, 0),
    "minecraft:sandstone": (24, 0),
    "minecraft:chiseled_sandstone": (24, 1),
    "minecraft:cut_sandstone": (24, 2),
    "minecraft:note_block": (25, 0),
    "minecraft:powered_rail": (27, 0),
    "minecraft:detector_rail": (28, 0),
    "minecraft:sticky_piston": (29, 0),
    "minecraft:cobweb": (30, 0),
    "minecraft:dead_bush": (32, 0),
    "minecraft:piston": (33, 0),
    "minecraft:dandelion": (37, 0),
    "minecraft:poppy": (38, 0),
    "minecraft:brown_mushroom": (39, 0),
    "minecraft:red_mushroom": (40, 0),
    "minecraft:gold_block": (41, 0),
    "minecraft:iron_block": (42, 0),
    "minecraft:bricks": (45, 0),
    "minecraft:tnt": (46, 0),
    "minecraft:bookshelf": (47, 0),
    "minecraft:mossy_cobblestone": (48, 0),
    "minecraft:obsidian": (49, 0),
    "minecraft:torch": (50, 0),
    "minecraft:lantern": (50, 0),
    "minecraft:fire": (51, 0),
    "minecraft:spawner": (52, 0),
    "minecraft:chest": (54, 0),
    "minecraft:redstone_wire": (55, 0),
    "minecraft:diamond_ore": (56, 0),
    "minecraft:diamond_block": (57, 0),
    "minecraft:crafting_table": (58, 0),
    "minecraft:wheat": (59, 0),
    "minecraft:farmland": (60, 0),
    "minecraft:furnace": (61, 0),
    "minecraft:ladder": (65, 0),
    "minecraft:rail": (66, 0),
    "minecraft:lever": (69, 0),
    "minecraft:stone_pressure_plate": (70, 0),
    "minecraft:oak_pressure_plate": (72, 0),
    "minecraft:redstone_ore": (73, 0),
    "minecraft:redstone_torch": (76, 0),
    "minecraft:stone_button": (77, 0),
    "minecraft:snow": (78, 0),
    "minecraft:ice": (79, 0),
    "minecraft:snow_block": (80, 0),
    "minecraft:cactus": (81, 0),
    "minecraft:clay": (82, 0),
    "minecraft:jukebox": (84, 0),
    "minecraft:oak_fence": (85, 0),
    "minecraft:pumpkin": (86, 0),
    "minecraft:netherrack": (87, 0),
    "minecraft:soul_sand": (88, 0),
    "minecraft:glowstone": (89, 0),
    "minecraft:jack_o_lantern": (91, 0),
    "minecraft:cake": (92, 0),
    "minecraft:trapdoor": (96, 0),
    "minecraft:oak_trapdoor": (96, 0),
    "minecraft:stone_bricks": (98, 0),
    "minecraft:stonebrick": (98, 0),
    "minecraft:mossy_stone_bricks": (98, 1),
    "minecraft:cracked_stone_bricks": (98, 2),
    "minecraft:chiseled_stone_bricks": (98, 3),
    "minecraft:iron_bars": (101, 0),
    "minecraft:glass_pane": (102, 0),
    "minecraft:melon": (103, 0),
    "minecraft:vine": (106, 0),
    "minecraft:mycelium": (110, 0),
    "minecraft:lily_pad": (111, 0),
    "minecraft:nether_bricks": (112, 0),
    "minecraft:nether_brick_fence": (113, 0),
    "minecraft:nether_wart": (115, 0),
    "minecraft:enchanting_table": (116, 0),
    "minecraft:brewing_stand": (117, 0),
    "minecraft:cauldron": (118, 0),
    "minecraft:end_stone": (121, 0),
    "minecraft:dragon_egg": (122, 0),
    "minecraft:redstone_lamp": (123, 0),
    "minecraft:emerald_ore": (129, 0),
    "minecraft:ender_chest": (130, 0),
    "minecraft:tripwire_hook": (131, 0),
    "minecraft:emerald_block": (133, 0),
    "minecraft:command_block": (137, 0),
    "minecraft:beacon": (138, 0),
    "minecraft:cobblestone_wall": (139, 0),
    "minecraft:mossy_cobblestone_wall": (139, 1),
    "minecraft:carrots": (141, 0),
    "minecraft:potatoes": (142, 0),
    "minecraft:oak_button": (143, 0),
    "minecraft:anvil": (145, 0),
    "minecraft:trapped_chest": (146, 0),
    "minecraft:light_weighted_pressure_plate": (147, 0),
    "minecraft:heavy_weighted_pressure_plate": (148, 0),
    "minecraft:redstone_block": (152, 0),
    "minecraft:nether_quartz_ore": (153, 0),
    "minecraft:hopper": (154, 0),
    "minecraft:quartz_block": (155, 0),
    "minecraft:chiseled_quartz_block": (155, 1),
    "minecraft:quartz_pillar": (155, 2),
    "minecraft:activator_rail": (157, 0),
    "minecraft:dropper": (158, 0),
    "minecraft:hay_block": (170, 0),
    "minecraft:hardened_clay": (172, 0),
    "minecraft:terracotta": (172, 0),
    "minecraft:coal_block": (173, 0),
    "minecraft:packed_ice": (174, 0),
    "minecraft:smooth_stone": (1, 0),
    "minecraft:deepslate": (4, 0),
    "minecraft:cobbled_deepslate": (4, 0),
    "minecraft:deepslate_bricks": (98, 0),
    "minecraft:polished_deepslate": (98, 0),
    "minecraft:blackstone": (4, 0),
}


def _parse_block(block: str) -> Tuple[str, Dict[str, str]]:
    match = re.match(r"^([^\[]+)(?:\[(.*)\])?$", block)
    if not match:
        return block, {}
    base = match.group(1)
    states_raw = match.group(2)
    states: Dict[str, str] = {}
    if states_raw:
        for item in states_raw.split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                states[key.strip()] = value.strip()
    return base, states


def _wood_variant(base: str, suffix: str) -> int:
    name = base.removeprefix("minecraft:")
    if not name.endswith(suffix):
        return 0
    variant = name[:-len(suffix)].rstrip("_")
    return WOOD_VARIANTS.get(variant, 0)


def _orient(states: Dict[str, str]) -> int:
    return {"south": 0, "west": 1, "north": 2, "east": 3}.get(states.get("facing", "south"), 0)


def _stairs_meta(states: Dict[str, str]) -> int:
    meta = {"east": 0, "west": 1, "south": 2, "north": 3}.get(states.get("facing", "north"), 3)
    if states.get("half") == "top":
        meta |= 4
    return meta


def _slab_meta(base: str, states: Dict[str, str], default_variant: int = 0) -> int:
    variant = _wood_variant(base, "_slab") if base.endswith("_slab") else default_variant
    variant = min(variant, 5)
    if states.get("type") == "top":
        variant |= 8
    return variant


def _log_meta(base: str, states: Dict[str, str]) -> Tuple[int, int]:
    variant = _wood_variant(base, "_log")
    block_id = 17
    if variant >= 4:
        block_id = 162
        variant -= 4
    if states.get("axis") == "x":
        variant |= 4
    elif states.get("axis") == "z":
        variant |= 8
    return block_id, variant


def legacy_id_data(block: str) -> Tuple[int, int]:
    base, states = _parse_block(block.strip())
    if not base.startswith("minecraft:"):
        base = f"minecraft:{base}"

    if base.endswith("_planks"):
        return 5, _wood_variant(base, "_planks")
    if base.endswith("_sapling"):
        return 6, _wood_variant(base, "_sapling")
    if base.endswith("_log"):
        return _log_meta(base, states)
    if base.endswith("_leaves"):
        variant = _wood_variant(base, "_leaves")
        if variant >= 4:
            return 161, variant - 4
        return 18, variant
    if base.endswith("_fence"):
        variant = _wood_variant(base, "_fence")
        return {0: 85, 1: 188, 2: 189, 3: 190, 4: 192, 5: 191}.get(variant, 85), 0
    if base.endswith("_fence_gate"):
        variant = _wood_variant(base, "_fence_gate")
        return {0: 107, 1: 183, 2: 184, 3: 185, 4: 187, 5: 186}.get(variant, 107), _orient(states)
    if base.endswith("_stairs"):
        block_id = {
            "minecraft:cobblestone_stairs": 67,
            "minecraft:stone_stairs": 67,
            "minecraft:brick_stairs": 108,
            "minecraft:stone_brick_stairs": 109,
            "minecraft:nether_brick_stairs": 114,
            "minecraft:sandstone_stairs": 128,
            "minecraft:quartz_stairs": 156,
        }.get(base)
        if block_id is None:
            variant = _wood_variant(base, "_stairs")
            block_id = {0: 53, 1: 134, 2: 135, 3: 136, 4: 163, 5: 164}.get(variant, 53)
        return block_id, _stairs_meta(states)
    if base.endswith("_slab"):
        stone_slab_types = {
            "minecraft:stone_slab": 0,
            "minecraft:smooth_stone_slab": 0,
            "minecraft:sandstone_slab": 1,
            "minecraft:cobblestone_slab": 3,
            "minecraft:brick_slab": 4,
            "minecraft:stone_brick_slab": 5,
            "minecraft:nether_brick_slab": 6,
            "minecraft:quartz_slab": 7,
        }
        if base in stone_slab_types:
            return 44, _slab_meta(base, states, stone_slab_types[base])
        return 126, _slab_meta(base, states)
    if base.endswith("_door"):
        return 64, _orient(states)
    if base.endswith("_wool"):
        return 35, COLORS.get(base.removeprefix("minecraft:").removesuffix("_wool"), 0)
    if base.endswith("_carpet"):
        return 171, COLORS.get(base.removeprefix("minecraft:").removesuffix("_carpet"), 0)
    if base.endswith("_stained_glass"):
        return 95, COLORS.get(base.removeprefix("minecraft:").removesuffix("_stained_glass"), 0)
    if base.endswith("_terracotta") or base.endswith("_concrete"):
        color = base.removeprefix("minecraft:").removesuffix("_terracotta").removesuffix("_concrete")
        if color in COLORS:
            return 159, COLORS[color]

    return BASE_BLOCKS.get(base, (1, 0))


def _write_name(fp, name: str) -> None:
    encoded = name.encode("utf-8")
    fp.write(struct.pack(">H", len(encoded)))
    fp.write(encoded)


def _write_named_short(fp, name: str, value: int) -> None:
    fp.write(struct.pack(">B", TAG_SHORT))
    _write_name(fp, name)
    fp.write(struct.pack(">h", value))


def _write_named_string(fp, name: str, value: str) -> None:
    encoded = value.encode("utf-8")
    fp.write(struct.pack(">B", TAG_STRING))
    _write_name(fp, name)
    fp.write(struct.pack(">H", len(encoded)))
    fp.write(encoded)


def _write_named_byte_array(fp, name: str, data: bytes) -> None:
    fp.write(struct.pack(">B", TAG_BYTE_ARRAY))
    _write_name(fp, name)
    fp.write(struct.pack(">i", len(data)))
    fp.write(data)


def _write_empty_compound_list(fp, name: str) -> None:
    fp.write(struct.pack(">B", TAG_LIST))
    _write_name(fp, name)
    fp.write(struct.pack(">B", TAG_COMPOUND))
    fp.write(struct.pack(">i", 0))


def write_legacy_schematic(placements: Iterable[Placement], path: str) -> str:
    blocks = list(placements)
    if not blocks:
        blocks = [(0, 0, 0, "minecraft:air")]

    min_x = min(x for x, _, _, _ in blocks)
    min_y = min(y for _, y, _, _ in blocks)
    min_z = min(z for _, _, z, _ in blocks)
    max_x = max(x for x, _, _, _ in blocks)
    max_y = max(y for _, y, _, _ in blocks)
    max_z = max(z for _, _, z, _ in blocks)

    width = max_x - min_x + 1
    height = max_y - min_y + 1
    length = max_z - min_z + 1

    if width > 32767 or height > 32767 or length > 32767:
        raise ValueError("Schematic dimensions are too large for the legacy MCEdit format")

    block_ids = bytearray(width * height * length)
    block_data = bytearray(width * height * length)

    for x, y, z, block in blocks:
        index = (y - min_y) * length * width + (z - min_z) * width + (x - min_x)
        block_id, data = legacy_id_data(block)
        block_ids[index] = block_id & 0xFF
        block_data[index] = data & 0x0F

    with gzip.open(path, "wb") as fp:
        fp.write(struct.pack(">B", TAG_COMPOUND))
        _write_name(fp, "Schematic")
        _write_named_short(fp, "Width", width)
        _write_named_short(fp, "Height", height)
        _write_named_short(fp, "Length", length)
        _write_named_string(fp, "Materials", "Alpha")
        _write_named_byte_array(fp, "Blocks", bytes(block_ids))
        _write_named_byte_array(fp, "Data", bytes(block_data))
        _write_empty_compound_list(fp, "Entities")
        _write_empty_compound_list(fp, "TileEntities")
        fp.write(struct.pack(">B", TAG_END))

    return path
