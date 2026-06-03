import gzip
import struct
from typing import Dict, List, Tuple

from .legacy_schematic import write_legacy_schematic

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

Placement = Tuple[int, int, int, str]


class _NBTReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def _read(self, size: int) -> bytes:
        if self.pos + size > len(self.data):
            raise ValueError("Unexpected end of NBT data")
        chunk = self.data[self.pos:self.pos + size]
        self.pos += size
        return chunk

    def read_ubyte(self) -> int:
        return struct.unpack(">B", self._read(1))[0]

    def read_byte(self) -> int:
        return struct.unpack(">b", self._read(1))[0]

    def read_short(self) -> int:
        return struct.unpack(">h", self._read(2))[0]

    def read_int(self) -> int:
        return struct.unpack(">i", self._read(4))[0]

    def read_long(self) -> int:
        return struct.unpack(">q", self._read(8))[0]

    def read_float(self) -> float:
        return struct.unpack(">f", self._read(4))[0]

    def read_double(self) -> float:
        return struct.unpack(">d", self._read(8))[0]

    def read_string(self) -> str:
        size = struct.unpack(">H", self._read(2))[0]
        return self._read(size).decode("utf-8")

    def read_payload(self, tag_type: int):
        if tag_type == TAG_BYTE:
            return self.read_byte()
        if tag_type == TAG_SHORT:
            return self.read_short()
        if tag_type == TAG_INT:
            return self.read_int()
        if tag_type == TAG_LONG:
            return self.read_long()
        if tag_type == TAG_FLOAT:
            return self.read_float()
        if tag_type == TAG_DOUBLE:
            return self.read_double()
        if tag_type == TAG_BYTE_ARRAY:
            size = self.read_int()
            return self._read(size)
        if tag_type == TAG_STRING:
            return self.read_string()
        if tag_type == TAG_LIST:
            item_type = self.read_ubyte()
            size = self.read_int()
            return [self.read_payload(item_type) for _ in range(size)]
        if tag_type == TAG_COMPOUND:
            result = {}
            while True:
                item_type = self.read_ubyte()
                if item_type == TAG_END:
                    break
                name = self.read_string()
                result[name] = self.read_payload(item_type)
            return result
        if tag_type == TAG_INT_ARRAY:
            size = self.read_int()
            return [self.read_int() for _ in range(size)]
        if tag_type == TAG_LONG_ARRAY:
            size = self.read_int()
            return [self.read_long() for _ in range(size)]
        raise ValueError(f"Unsupported NBT tag type: {tag_type}")


def _read_nbt(path: str) -> Dict:
    with open(path, "rb") as fp:
        raw = fp.read()

    try:
        data = gzip.decompress(raw)
    except OSError:
        data = raw

    reader = _NBTReader(data)
    tag_type = reader.read_ubyte()
    if tag_type != TAG_COMPOUND:
        raise ValueError("Root NBT tag must be a compound")

    reader.read_string()
    root = reader.read_payload(TAG_COMPOUND)
    if not isinstance(root, dict):
        raise ValueError("Root NBT payload must be a compound")
    return root


def _decode_varints(data: bytes) -> List[int]:
    values: List[int] = []
    value = 0
    shift = 0

    for byte in data:
        value |= (byte & 0x7F) << shift
        if (byte & 0x80) == 0:
            values.append(value)
            value = 0
            shift = 0
        else:
            shift += 7
            if shift > 35:
                raise ValueError("Invalid varint in BlockData")

    if shift != 0:
        raise ValueError("Truncated varint in BlockData")

    return values


def read_schem_placements(path: str) -> List[Placement]:
    root = _read_nbt(path)

    palette = root.get("Palette")
    block_data = root.get("BlockData")
    width = root.get("Width")
    height = root.get("Height")
    length = root.get("Length")

    if not isinstance(palette, dict) or not isinstance(block_data, bytes):
        raise ValueError("Only Sponge .schem files with Palette and BlockData are supported")
    if not isinstance(width, int) or not isinstance(height, int) or not isinstance(length, int):
        raise ValueError("Schematic Width, Height and Length tags must be present")

    index_to_block: Dict[int, str] = {}
    for block, index in palette.items():
        if isinstance(block, str) and isinstance(index, int):
            index_to_block[index] = block

    palette_indices = _decode_varints(block_data)
    expected_size = width * height * length
    if len(palette_indices) < expected_size:
        raise ValueError("BlockData contains fewer blocks than expected")

    placements: List[Placement] = []
    layer_size = width * length

    for index, palette_index in enumerate(palette_indices[:expected_size]):
        block = index_to_block.get(palette_index, "minecraft:air")
        if block == "minecraft:air":
            continue
        x = index % width
        z = (index // width) % length
        y = index // layer_size
        placements.append((x, y, z, block))

    return placements


def convert_schem_file_to_legacy(input_path: str, output_path: str) -> str:
    placements = read_schem_placements(input_path)
    return write_legacy_schematic(placements, output_path)
