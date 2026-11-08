#!/usr/bin/env python3
"""
Scroll-Driven CSS Generator

Generates native CSS for a scroll-driven effect, optionally wrapped in a
@supports (animation-timeline: ...) block with a visible static fallback.

Usage:
    ./generate_scroll_css.py                                  # interactive
    ./generate_scroll_css.py --effect reveal --selector ".card"
    ./generate_scroll_css.py --effect progress --selector ".progress"
    ./generate_scroll_css.py --effect parallax --no-supports
    ./generate_scroll_css.py --effect sticky-clip --output src/effect.css

Effects:
    progress     - fixed top progress bar tied to page scroll
    reveal       - fade + rise as the element enters the viewport
    parallax     - slow vertical drift while in view
    sticky-clip  - clip-path reveal on a sticky element
    horizontal   - horizontal row driven by vertical page scroll
    tint         - background color shift with page scroll

Dependencies: Python 3 standard library only.
"""

import argparse
import sys

# Each effect: (keyframes, declarations, timeline_kind)
# timeline_kind picks the @supports feature test (scroll() or view()).
EFFECTS = {
    'progress': (
        '@keyframes sd-grow { to { transform: scaleX(1); } }',
        'position: fixed;\n  inset: 0 0 auto 0;\n  height: 4px;\n  background: #7b5cff;\n'
        '  transform: scaleX(0);\n  transform-origin: left;\n'
        '  animation: sd-grow auto linear;\n  animation-timeline: scroll(root);',
        'scroll',
        '',  # fallback extra (none)
    ),
    'reveal': (
        '@keyframes sd-reveal { from { opacity: 0; translate: 0 2rem; } to { opacity: 1; translate: 0 0; } }',
        'animation: sd-reveal linear both;\n  animation-timeline: view();\n'
        '  animation-range: entry 0% cover 30%;',
        'view',
        'opacity: 0;',  # hide only inside @supports
    ),
    'parallax': (
        '@keyframes sd-parallax { to { translate: 0 -18%; } }',
        'animation: sd-parallax linear;\n  animation-timeline: view();\n'
        '  animation-range: cover;',
        'view',
        '',
    ),
    'sticky-clip': (
        '@keyframes sd-unclip { from { clip-path: inset(45%); } to { clip-path: inset(0%); } }',
        'position: sticky;\n  top: 0;\n  animation: sd-unclip linear both;\n'
        '  animation-timeline: view();\n  animation-range: entry 0% cover 50%;',
        'view',
        '',
    ),
    'horizontal': (
        '@keyframes sd-slide { to { transform: translateX(-66%); } }',
        'display: flex;\n  animation: sd-slide auto linear;\n'
        '  animation-timeline: scroll(root);',
        'scroll',
        '',
    ),
    'tint': (
        '@keyframes sd-tint { from { background: #0b0b12; } to { background: #1b1030; } }',
        'animation: sd-tint auto linear;\n  animation-timeline: scroll(root);',
        'scroll',
        '',
    ),
}


def build(effect: str, selector: str, with_supports: bool) -> str:
    keyframes, decls, kind, fallback = EFFECTS[effect]
    feature = 'scroll()' if kind == 'scroll' else 'view()'

    # Declarations that only apply when the feature is supported. A `fallback`
    # (e.g. opacity: 0) must live inside @supports so it never hides content in
    # unsupported browsers.
    enhanced = (fallback + '\n  ' + decls) if fallback else decls

    if with_supports:
        return (
            f'{keyframes}\n\n'
            f'{selector} {{\n  /* visible static fallback for unsupported browsers */\n}}\n\n'
            f'@supports (animation-timeline: {feature}) {{\n'
            f'  {selector} {{\n  {enhanced}\n  }}\n'
            f'}}\n'
        )
    return f'{keyframes}\n\n{selector} {{\n  {enhanced}\n}}\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate scroll-driven CSS.')
    parser.add_argument('--effect', choices=sorted(EFFECTS), help='Effect preset')
    parser.add_argument('--selector', default='.target', help='CSS selector to target')
    parser.add_argument('--no-supports', action='store_true',
                        help='Skip the @supports fallback wrapper')
    parser.add_argument('--output', help='Write to a file instead of stdout')
    args = parser.parse_args()

    effect = args.effect
    if not effect:
        print('Available effects: ' + ', '.join(sorted(EFFECTS)))
        try:
            effect = input('Choose effect [reveal]: ').strip() or 'reveal'
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        if effect not in EFFECTS:
            print(f"Error: unknown effect '{effect}'", file=sys.stderr)
            return 1

    css = build(effect, args.selector, not args.no_supports)

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(css)
            print(f'Wrote {effect} CSS to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(css)
    return 0


if __name__ == '__main__':
    sys.exit(main())
