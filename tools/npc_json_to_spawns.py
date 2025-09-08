import json
import math
import os
import struct
import sys
import urllib.request
from urllib.error import URLError, HTTPError

# Default input: OSRS NPC list JSON (world coords + id)
DEFAULT_URL = (
    "https://raw.githubusercontent.com/mejrs/data_osrs/64b07f2173a657a79089f13a30051c8e6b768b0b/NPCList_OSRS.json"
)

# Default output directory inside this repo (per server expectations)
# Files will be written as content/areas/external/src/main/resources/map/nX_Z
DEFAULT_OUT_DIR = os.path.join(
    "content", "areas", "external", "src", "main", "resources", "map"
)


def pack_spawn(npc_id: int, local_x: int, local_z: int, level: int) -> int:
    """Pack spawn into 32-bit value: id(16) | localZ(6) | localX(6) | level(2)."""
    if not (0 <= npc_id <= 0xFFFF):
        raise ValueError(f"id out of range: {npc_id}")
    if not (0 <= local_x <= 63 and 0 <= local_z <= 63):
        raise ValueError(f"local coords out of range: {local_x},{local_z}")
    if not (0 <= level <= 3):
        raise ValueError(f"level out of range: {level}")
    packed = (
        ((npc_id & 0xFFFF) << 0)
        | ((local_z & 0x3F) << 16)
        | ((local_x & 0x3F) << 22)
        | ((level & 0x3) << 28)
    )
    return packed


def load_json(source: str):
    """Load JSON from URL or local file path."""
    if source.startswith("http://") or source.startswith("https://"):
        try:
            with urllib.request.urlopen(source) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (URLError, HTTPError) as e:
            raise SystemExit(f"Failed to fetch URL: {source}\n{e}")
    # Local file path
    with open(source, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # Args: [json_url_or_path] [out_dir]
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    out_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_DIR

    os.makedirs(out_dir, exist_ok=True)

    data = load_json(src)

    # Group by map square (squareX, squareZ)
    squares: dict[tuple[int, int], list[int]] = {}

    count_total = 0
    for e in data:
        npc_id = e.get("id")
        x = e.get("x")
        z = e.get("y")
        level = e.get("p", 0)
        if npc_id is None or x is None or z is None:
            continue
        sx, sz = x // 64, z // 64
        lx, lz = x % 64, z % 64
        packed = pack_spawn(int(npc_id), int(lx), int(lz), int(level))
        squares.setdefault((int(sx), int(sz)), []).append(packed)
        count_total += 1

    # Write per-square files: big-endian short count, then count * big-endian int
    for (sx, sz), spawns in squares.items():
        path = os.path.join(out_dir, f"n{sx}_{sz}")
        if len(spawns) > 65535:
            raise ValueError(f"Too many spawns for square {sx},{sz}: {len(spawns)}")
        with open(path, "wb") as f:
            f.write(struct.pack(">H", len(spawns)))
            for p in spawns:
                f.write(struct.pack(">I", p))
        print(f"Wrote {path} ({len(spawns)} spawns)")

    print(f"Done. Total spawns: {count_total}. Squares: {len(squares)}. Output: {out_dir}")


if __name__ == "__main__":
    main()
