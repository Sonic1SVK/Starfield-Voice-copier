"""
Post-processing for Champollion output targeting Starfield.

Champollion's Starfield support is good but not perfect. This module applies
SAFE, non-destructive cleanup and reports constructs that need manual review
before you try compiling.
"""
import re
from pathlib import Path


WARNING_PATTERNS = [
    (re.compile(r"^\s*Guard\b", re.MULTILINE),
     "Guard block found – Starfield accepts Guard/EndGuard, verify it compiles"),
    (re.compile(r"^\s*TryGuard\b", re.MULTILINE),
     "TryGuard block found – verify your Papyrus compiler accepts it"),
    (re.compile(r"\bArrayGetAllMatchingStructs\b"),
     "ArrayGetAllMatchingStructs – not supported in all Starfield versions"),
    (re.compile(r"^\s*Struct\s+\w+\s*$", re.MULTILINE),
     "Struct declaration – verify field types are explicit for Starfield"),
    (re.compile(r"^\s*CustomEvent\b", re.MULTILINE),
     "CustomEvent – verify Starfield Papyrus handles it as expected"),
]


def fix_source(source: str) -> tuple[str, list[str], list[str]]:
    """
    Returns (fixed_source, changes_applied, warnings).
    """
    changes: list[str] = []
    warnings: list[str] = []

    original = source

    # 1. Strip UTF-8 BOM
    if source.startswith("\ufeff"):
        source = source[1:]
        changes.append("removed UTF-8 BOM")

    # 2. Normalize line endings
    if "\r\n" in source:
        source = source.replace("\r\n", "\n")
        changes.append("normalized CRLF → LF")
    if "\r" in source:
        source = source.replace("\r", "\n")
        changes.append("normalized CR → LF")

    # 3. Strip trailing whitespace per line
    lines = source.split("\n")
    stripped = [ln.rstrip() for ln in lines]
    if stripped != lines:
        changes.append("stripped trailing whitespace")
        source = "\n".join(stripped)

    # 4. Ensure final newline
    if source and not source.endswith("\n"):
        source += "\n"
        changes.append("added final newline")

    # 5. Collapse 3+ consecutive blank lines to 2
    before = source
    source = re.sub(r"\n{3,}", "\n\n", source)
    if source != before:
        changes.append("collapsed excess blank lines")

    # 6. Sanity check: ScriptName should be the first meaningful token
    if "ScriptName" not in source:
        warnings.append("⚠ No 'ScriptName' declaration found – file may not compile")
    else:
        first_meaningful = None
        for ln in source.split("\n"):
            s = ln.strip()
            if not s or s.startswith(";"):
                continue
            first_meaningful = s
            break
        if first_meaningful and not first_meaningful.startswith("ScriptName"):
            warnings.append(
                f"⚠ First declaration is not 'ScriptName' but: {first_meaningful[:60]}"
            )

    # 7. Pattern-based warnings (do NOT rewrite – too risky across versions)
    for pattern, msg in WARNING_PATTERNS:
        if pattern.search(source):
            warnings.append(f"⚠ {msg}")

    return source, changes, warnings


def process_file(path: Path) -> tuple[list[str], list[str]]:
    """Post-process a .psc file in place. Returns (changes, warnings)."""
    try:
        original = path.read_text(encoding="utf-8")
    except Exception as e:
        return [], [f"✗ Could not read {path.name}: {e}"]

    fixed, changes, warnings = fix_source(original)

    if fixed != original:
        try:
            path.write_text(fixed, encoding="utf-8", newline="\n")
        except Exception as e:
            return changes, warnings + [f"✗ Could not write {path.name}: {e}"]

    return changes, warnings
