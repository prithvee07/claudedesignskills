#!/usr/bin/env python3
"""
Matter.js Body Generator

Generates a `Bodies.*` creation call for a shape with common options, ready to
paste into a Matter.js setup.

Usage:
    ./generate_body.py --shape rectangle --x 400 --y 100 --w 80 --h 80
    ./generate_body.py --shape circle --x 200 --y 50 --r 30 --restitution 0.8 --color "#ff4dd8"
    ./generate_body.py --shape polygon --sides 6 --r 40 --static
    ./generate_body.py              # interactive

Shapes:
    rectangle - needs --w and --h
    circle    - needs --r
    polygon   - needs --sides and --r

Dependencies: Python 3 standard library only.
"""

import argparse
import sys


def fmt(v) -> str:
    """Render whole floats as ints (200.0 -> 200) for cleaner output."""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def options_str(restitution, friction, static, color) -> str:
    opts = []
    if static:
        opts.append('isStatic: true')
    if restitution is not None:
        opts.append(f'restitution: {fmt(restitution)}')
    if friction is not None:
        opts.append(f'friction: {fmt(friction)}')
    if color:
        opts.append(f"render: {{ fillStyle: '{color}' }}")
    if not opts:
        return ''
    return '{ ' + ', '.join(opts) + ' }'


def build(args) -> str:
    opts = options_str(args.restitution, args.friction, args.static, args.color)
    tail = f', {opts}' if opts else ''
    x, y = fmt(args.x), fmt(args.y)
    if args.shape == 'rectangle':
        if args.w is None or args.h is None:
            raise ValueError('rectangle requires --w and --h')
        return f'const body = Bodies.rectangle({x}, {y}, {fmt(args.w)}, {fmt(args.h)}{tail})\n'
    if args.shape == 'circle':
        if args.r is None:
            raise ValueError('circle requires --r')
        return f'const body = Bodies.circle({x}, {y}, {fmt(args.r)}{tail})\n'
    if args.shape == 'polygon':
        if args.sides is None or args.r is None:
            raise ValueError('polygon requires --sides and --r')
        return f'const body = Bodies.polygon({x}, {y}, {args.sides}, {fmt(args.r)}{tail})\n'
    raise ValueError(f'unknown shape: {args.shape}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a Matter.js body.')
    parser.add_argument('--shape', choices=['rectangle', 'circle', 'polygon'])
    parser.add_argument('--x', type=float, default=400)
    parser.add_argument('--y', type=float, default=100)
    parser.add_argument('--w', type=float, default=None)
    parser.add_argument('--h', type=float, default=None)
    parser.add_argument('--r', type=float, default=None)
    parser.add_argument('--sides', type=int, default=None)
    parser.add_argument('--restitution', type=float, default=None)
    parser.add_argument('--friction', type=float, default=None)
    parser.add_argument('--static', action='store_true')
    parser.add_argument('--color', default=None)
    parser.add_argument('--output', help='Write to a file instead of stdout')
    args = parser.parse_args()

    if not args.shape:
        try:
            args.shape = input('Shape [rectangle/circle/polygon] (rectangle): ').strip() or 'rectangle'
            if args.shape not in ('rectangle', 'circle', 'polygon'):
                print(f"Error: unknown shape '{args.shape}'", file=sys.stderr)
                return 1
            if args.shape == 'rectangle':
                args.w = float(input('Width [80]: ').strip() or 80)
                args.h = float(input('Height [80]: ').strip() or 80)
            else:
                args.r = float(input('Radius [30]: ').strip() or 30)
                if args.shape == 'polygon':
                    args.sides = int(input('Sides [6]: ').strip() or 6)
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        except ValueError:
            print('Error: numeric fields must be numbers', file=sys.stderr)
            return 1

    try:
        code = build(args)
    except ValueError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(code)
            print(f'Wrote body to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(code)
    return 0


if __name__ == '__main__':
    sys.exit(main())
