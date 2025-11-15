#!/usr/bin/env python3


import math, random, hashlib, csv, argparse, os, json
from datetime import datetime, timezone

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"

class Perlin1D:
    def __init__(self, seed=0):
        rnd = random.Random(seed)
        p = list(range(256))
        rnd.shuffle(p)
        self.perm = p + p

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def grad(self, hash_val, x):
        h = hash_val & 15
        grad = 1 + (h % 8)
        if (h & 8) != 0:
            grad = -grad
        return grad * x

    def lerp(self, a, b, t):
        return a + t * (b - a)

    def noise(self, x):
        xi = math.floor(x) & 255
        xf = x - math.floor(x)
        u = self.fade(xf)
        a = self.perm[xi]
        b = self.perm[xi + 1]
        g1 = self.grad(a, xf)
        g2 = self.grad(b, xf - 1)
        return self.lerp(g1, g2, u)

    def sample_bytes(self, start=0.0, step=0.5, n=8):
        vals = []
        minv, maxv = float('inf'), float('-inf')
        for i in range(n):
            v = self.noise(start + i * step)
            vals.append(v)
            if v < minv: minv = v
            if v > maxv: maxv = v
        if maxv - minv < 1e-9:
            normalized = [128] * n
        else:
            normalized = [int(255 * ( (v - minv) / (maxv - minv) )) for v in vals]
        return bytes(normalized)

def to_base36(b: bytes) -> str:
    x = int.from_bytes(b, byteorder='big', signed=False)
    if x == 0:
        return "0"
    digits = []
    while x:
        x, rem = divmod(x, 36)
        digits.append(ALPHABET[rem])
    return ''.join(reversed(digits))

def deterministic_hash(value: str, salt: str = "") -> int:
    h = hashlib.sha256((value + salt).encode('utf8')).digest()
    return int.from_bytes(h[:8], 'big')

def generate_perlin_chunk_seeded(seed: int, chunk_bytes=6, start=0.0, step=0.5):
    p = Perlin1D(seed=seed)
    b = p.sample_bytes(start=start, step=step, n=chunk_bytes)
    return to_base36(b)

def generate_honeytoken(template: str, seed_source: str, variant:int=0, chunk_bytes=6):
    seed_val = deterministic_hash(seed_source + f":{variant}")
    chunk = generate_perlin_chunk_seeded(seed_val, chunk_bytes=chunk_bytes,
                                         start=variant * 0.37, step=0.41)
    chunk_short = chunk[:10]
    token = template.replace("{PN}", chunk_short)
    return token, seed_val

def build_exact_match_regex_for_templates(templates):
    import re
    escaped = []
    for t in templates:
        pattern = re.escape(t).replace("\\{PN\\}", r"[0-9a-z]{4,12}")
        escaped.append(pattern)
    combined = "(" + "|".join(escaped) + ")"
    return combined  # return string pattern for user

def write_registry_csv(entries, out_path):
    fieldnames = ["token","template","entity","dept","seed_int","variant","created_at","tags"]
    with open(out_path, "w", newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in entries:
            writer.writerow(e)

def main():
    parser = argparse.ArgumentParser(description="Perlin Honeytoken Generator")
    parser.add_argument("--entity", "-e", required=True, help="Entity name (e.g., 'Atlas')")
    parser.add_argument("--dept", "-d", required=True, help="Department or domain (e.g., 'Finance')")
    parser.add_argument("--count", "-c", type=int, default=10, help="Total number of honeytokens to generate")
    parser.add_argument("--variants", "-v", type=int, default=3, help="Variants per template")
    parser.add_argument("--out", "-o", default="perlin_honeytokens.csv", help="Output CSV path")
    parser.add_argument("--seed-note", "-s", default="", help="Optional extra seed note for provenance")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    templates = [
        "{ENTITY}-{DEPT}-PN{PN}-{YY}",
        "{DEPT}-{ENTITY}-Key-PN{PN}",
        "Acct-{DEPT}-PN{PN}"
    ]

    entries = []
    generated = 0
    template_i = 0
    while generated < args.count:
        for t in templates:
            if generated >= args.count:
                break
            entity = args.entity
            dept = args.dept
            yy = now.strftime('%y')
            templ_full = t.replace("{ENTITY}", entity).replace("{DEPT}", dept).replace("{YY}", yy)
            for v in range(args.variants):
                if generated >= args.count:
                    break
                seed_source = f"{entity}|{dept}|{now.isoformat()}|variant{v}|{args.seed_note}"
                token, seed_val = generate_honeytoken(templ_full, seed_source, variant=v)
                entries.append({
                    "token": token,
                    "template": t,
                    "entity": entity,
                    "dept": dept,
                    "seed_int": seed_val,
                    "variant": v,
                    "created_at": now.isoformat(),
                    "tags": "perlin,auto"
                })
                generated += 1
                if generated >= args.count:
                    break

    write_registry_csv(entries, args.out)
    pattern = build_exact_match_regex_for_templates(templates)
    print(f"Generated {len(entries)} tokens. Registry written to: {os.path.abspath(args.out)}")
    print("\nExample tokens:")
    for e in entries[:min(10,len(entries))]:
        print(" -", e["token"])
    print("\nDetection regex (use with case-insensitive search):")
    print(pattern)

if __name__ == "__main__":
    main()
