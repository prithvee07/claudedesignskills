#!/usr/bin/env python3
"""
Theatre.js Production Readiness Checker

Scans JavaScript/TypeScript source for common Theatre.js footguns that cause
bloated bundles or runtime glitches in production:

  1. studio.initialize() / studio.extend() not guarded by a dev check
  2. @theatre/studio listed under "dependencies" instead of "devDependencies"
  3. A project loaded with { state } but no `project.ready` await/then nearby
  4. Duplicate getProject('<name>') project names across files

Exit codes:
    0 - no issues found
    1 - one or more issues found
    2 - usage / path error

Usage:
    ./check_production_ready.py            # scan current directory
    ./check_production_ready.py ./src      # scan a specific directory
    ./check_production_ready.py app.js     # scan a single file

Dependencies: Python 3 standard library only.
"""

import argparse
import json
import os
import re
import sys

SOURCE_EXTS = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '.next', 'out', 'coverage'}

GUARD_HINTS = ('import.meta.env', 'NODE_ENV', 'process.env', 'if (', 'DEV')


def iter_source_files(root: str):
    """Yield source file paths under root (or root itself if it's a file)."""
    if os.path.isfile(root):
        if os.path.splitext(root)[1] in SOURCE_EXTS:
            yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1] in SOURCE_EXTS:
                yield os.path.join(dirpath, name)


def line_is_guarded(lines, idx: int) -> bool:
    """Heuristic: a studio call is guarded if a dev condition sits on the same
    line or within the preceding 3 lines."""
    window = lines[max(0, idx - 3):idx + 1]
    text = '\n'.join(window)
    return any(hint in text for hint in GUARD_HINTS)


def check_file(path: str, issues: list, projects: dict):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        issues.append((path, 0, f'could not read file: {exc}'))
        return

    full = '\n'.join(lines)
    has_ready = 'project.ready' in full or '.ready' in full

    for i, line in enumerate(lines):
        # 1. Unguarded studio calls
        if re.search(r'\bstudio\.(initialize|extend)\s*\(', line):
            if not line_is_guarded(lines, i):
                issues.append((path, i + 1,
                               'studio call not guarded by a dev check '
                               '(may ship Studio to production)'))

        # 3. state load without a nearby ready await
        if re.search(r'getProject\s*\([^)]*\{\s*state', line) and not has_ready:
            issues.append((path, i + 1,
                           'project loaded with { state } but no project.ready '
                           'await/then found in this file'))

        # 4. collect project names
        for m in re.finditer(r"getProject\s*\(\s*['\"]([^'\"]+)['\"]", line):
            projects.setdefault(m.group(1), []).append(f'{path}:{i + 1}')


def check_package_json(root: str, issues: list):
    """Flag @theatre/studio in runtime dependencies."""
    pkg = root if os.path.basename(root) == 'package.json' else os.path.join(
        root if os.path.isdir(root) else os.path.dirname(root), 'package.json')
    if not os.path.isfile(pkg):
        return
    try:
        with open(pkg, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return
    if '@theatre/studio' in (data.get('dependencies') or {}):
        issues.append((pkg, 0,
                       '@theatre/studio is in "dependencies"; move it to '
                       '"devDependencies" so it is excluded from production'))


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Check a Theatre.js project for production footguns.')
    parser.add_argument('path', nargs='?', default='.',
                        help='File or directory to scan (default: .)')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f'Error: path not found: {args.path}', file=sys.stderr)
        return 2

    issues: list = []
    projects: dict = {}

    for src in iter_source_files(args.path):
        check_file(src, issues, projects)

    check_package_json(args.path, issues)

    # 4. duplicate project names across DIFFERENT files (in-file reuse of the
    #    memoized handle is legitimate, so only cross-file collisions are flagged)
    for name, locations in projects.items():
        files = {loc.rsplit(':', 1)[0] for loc in locations}
        if len(files) > 1:
            issues.append((locations[0].rsplit(':', 1)[0], 0,
                           f"project name '{name}' used across multiple files: "
                           f"{', '.join(locations)} (getProject is memoized by "
                           f"name; unique names avoid cross-file state collisions)"))

    if not issues:
        print('✅ No production-readiness issues found.')
        return 0

    print(f'⚠️  Found {len(issues)} issue(s):\n')
    for path, line, msg in issues:
        where = f'{path}:{line}' if line else path
        print(f'  {where}\n    {msg}\n')
    return 1


if __name__ == '__main__':
    sys.exit(main())
