#!/usr/bin/env python3
"""validate_skill.py — 轻量 skill frontmatter 验证

用法:
  python3 scripts/validate_skill.py [skill目录]

默认验证当前目录。
"""

import re
import sys
from pathlib import Path

ALLOWED_PROPERTIES = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}


def validate_skill(skill_path: Path):
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter = match.group(1)
    # 只提取顶层 key（缩进的不算）
    keys = set(re.findall(r"^(\w+):", frontmatter, re.MULTILINE))
    unexpected = keys - ALLOWED_PROPERTIES
    if unexpected:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    if "name" not in keys:
        return False, "Missing 'name' in frontmatter"
    if "description" not in keys:
        return False, "Missing 'description' in frontmatter"

    return True, "Skill is valid"


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    valid, message = validate_skill(path)
    print(message)
    sys.exit(0 if valid else 1)
