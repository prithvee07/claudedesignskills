#!/usr/bin/env python3
"""
Lenis Config Generator

Builds a `new Lenis({...})` options object from flags or interactive prompts,
including a named easing function. Useful for quickly producing a tuned config.

Usage:
    ./generate_config.py                                  # interactive
    ./generate_config.py --duration 1.4 --easing expo
    ./generate_config.py --orientation horizontal --lerp 0.08
    ./generate_config.py --easing cubic --reduced-motion

Easings:
    expo  - exponential out (default, punchy)
    cubic - cubic out (gentle)
    quint - quintic out (very smooth)
    linear

Dependencies: Python 3 standard library only.
"""

import argparse
import sys

EASINGS = {
    'expo': '(t) => Math.min(1, 1.001 - Math.pow(2, -10 * t))',
    'cubic': '(t) => 1 - Math.pow(1 - t, 3)',
    'quint': '(t) => 1 - Math.pow(1 - t, 5)',
    'linear': '(t) => t',
}


def build(duration, lerp, easing, orientation, gesture, wheel_mult,
          touch_mult, reduced_motion) -> str:
    lines = []
    if reduced_motion:
        lines.append("const prefersReduced = "
                     "window.matchMedia('(prefers-reduced-motion: reduce)').matches")
        lines.append('')

    opts = []
    if lerp is not None:
        opts.append(f'  lerp: {lerp},')
    else:
        dur = f'prefersReduced ? 0 : {duration}' if reduced_motion else f'{duration}'
        opts.append(f'  duration: {dur},')
        opts.append(f'  easing: {EASINGS[easing]},')
    opts.append(f"  orientation: '{orientation}',")
    opts.append(f"  gestureOrientation: '{gesture}',")
    if reduced_motion:
        opts.append('  smoothWheel: !prefersReduced,')
    if wheel_mult != 1:
        opts.append(f'  wheelMultiplier: {wheel_mult},')
    if touch_mult != 1:
        opts.append(f'  touchMultiplier: {touch_mult},')

    lines.append('const lenis = new Lenis({')
    lines.extend(opts)
    lines.append('})')
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a Lenis config object.')
    parser.add_argument('--duration', type=float, default=1.2)
    parser.add_argument('--lerp', type=float, default=None,
                        help='Use lerp instead of duration/easing')
    parser.add_argument('--easing', choices=sorted(EASINGS), default='expo')
    parser.add_argument('--orientation', choices=['vertical', 'horizontal'],
                        default='vertical')
    parser.add_argument('--gesture', choices=['vertical', 'horizontal', 'both'],
                        default='vertical')
    parser.add_argument('--wheel-mult', type=float, default=1)
    parser.add_argument('--touch-mult', type=float, default=1)
    parser.add_argument('--reduced-motion', action='store_true',
                        help='Add a prefers-reduced-motion guard')
    parser.add_argument('--output', help='Write to file instead of stdout')
    args = parser.parse_args()

    # Interactive only if no meaningful flags and stdin is a tty
    interactive = (len(sys.argv) == 1) and sys.stdin.isatty()
    if interactive:
        try:
            d = input('Duration in seconds [1.2]: ').strip()
            if d:
                args.duration = float(d)
            e = input(f"Easing {sorted(EASINGS)} [expo]: ").strip()
            if e:
                if e not in EASINGS:
                    print(f"Error: unknown easing '{e}'", file=sys.stderr)
                    return 1
                args.easing = e
            o = input('Orientation [vertical]: ').strip()
            if o:
                if o not in ('vertical', 'horizontal'):
                    print(f"Error: invalid orientation '{o}'", file=sys.stderr)
                    return 1
                args.orientation = o
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        except ValueError:
            print('Error: duration must be a number', file=sys.stderr)
            return 1

    code = build(args.duration, args.lerp, args.easing, args.orientation,
                 args.gesture, args.wheel_mult, args.touch_mult,
                 args.reduced_motion)

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(code)
            print(f'Wrote config to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(code)
    return 0


if __name__ == '__main__':
    sys.exit(main())
