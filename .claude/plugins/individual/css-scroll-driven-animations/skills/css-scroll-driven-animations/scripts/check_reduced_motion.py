#!/usr/bin/env python3
"""
Reduced-Motion Guard Generator

Emits a `@media (prefers-reduced-motion: reduce)` block that neutralizes
scroll-driven animations for the given selectors, so motion-sensitive users get
a static, readable page.

Usage:
    ./check_reduced_motion.py --selectors ".reveal,.parallax,.sticky-img"
    ./check_reduced_motion.py --selectors ".card" --output src/a11y.css
    ./check_reduced_motion.py            # interactive

The generated block resets animation and common animated properties.

Dependencies: Python 3 standard library only.
"""

import argparse
import sys


def build(selectors: list) -> str:
    sel = ',\n  '.join(selectors)
    return (
        '@media (prefers-reduced-motion: reduce) {\n'
        f'  {sel} {{\n'
        '    animation: none !important;\n'
        '    opacity: 1 !important;\n'
        '    transform: none !important;\n'
        '    translate: none !important;\n'
        '    clip-path: none !important;\n'
        '  }\n'
        '}\n'
    )


def parse_selectors(raw: str) -> list:
    selectors = [s.strip() for s in raw.split(',') if s.strip()]
    if not selectors:
        raise ValueError('no selectors provided')
    return selectors


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Generate a prefers-reduced-motion guard for scroll effects.')
    parser.add_argument('--selectors',
                        help='Comma-separated CSS selectors to neutralize')
    parser.add_argument('--output', help='Write to a file instead of stdout')
    args = parser.parse_args()

    raw = args.selectors
    if not raw:
        try:
            raw = input('Selectors (comma-separated) [.reveal,.parallax]: ').strip() \
                or '.reveal,.parallax'
        except (EOFError, KeyboardInterrupt):
            print()
            return 1

    try:
        selectors = parse_selectors(raw)
    except ValueError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1

    css = build(selectors)

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(css)
            print(f'Wrote reduced-motion guard to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(css)
    return 0


if __name__ == '__main__':
    sys.exit(main())
