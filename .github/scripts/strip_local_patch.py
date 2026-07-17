#!/usr/bin/env python3
"""Strip the local [patch] override for jwalk-meta so CI uses the git dependency.

Local development keeps a ``[patch."<URL>"]`` section in the workspace
``Cargo.toml`` that overrides the git dependency declared in
``scandir/Cargo.toml`` with a path dependency (``../jwalk-meta``). On CI that
path does not exist, so this script removes the section before cargo/maturin
runs. Safe to run when the section is already absent (idempotent).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATCH_URL = "https://github.com/Be90nia/jwalk-meta"
# Match an optional leading comment block (consecutive ``# ...`` lines) plus
# the ``[patch."<URL>"]`` table header, plus every line until the next
# section header (line starting with ``[``) or end of file. Non-greedy so it
# stops at the first following section.
SECTION_RE = re.compile(
    r'\n+(?:# [^\n]*\n+)*\[patch\."' + re.escape(PATCH_URL) + r'"\]\n.*?(?=\n\[|\Z)',
    re.DOTALL,
)


def strip(cargo_toml: Path) -> bool:
    original = cargo_toml.read_text(encoding="utf-8")
    stripped = SECTION_RE.sub("\n", original)
    # Tidy up excessive blank lines left behind, then ensure a single trailing newline.
    stripped = re.sub(r"\n\n\n+", "\n\n", stripped).rstrip() + "\n"
    if stripped == original:
        return False
    cargo_toml.write_text(stripped, encoding="utf-8")
    return True


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("Cargo.toml")
    if not target.exists():
        print(f"error: {target} not found", file=sys.stderr)
        return 2
    changed = strip(target)
    print(f"{target}: {'patch stripped' if changed else 'no patch present'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
