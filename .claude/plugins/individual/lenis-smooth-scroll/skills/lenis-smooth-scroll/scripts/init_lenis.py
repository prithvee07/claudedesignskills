#!/usr/bin/env python3
"""
Lenis Smooth Scroll Boilerplate Generator

Generates ready-to-use Lenis setup code for one of three presets, each wiring a
single RAF loop and (where relevant) integration glue.

Usage:
    ./init_lenis.py                      # interactive mode
    ./init_lenis.py --preset vanilla     # core Lenis + RAF loop
    ./init_lenis.py --preset gsap        # Lenis driven by GSAP ticker + ScrollTrigger
    ./init_lenis.py --preset react       # ReactLenis provider + useLenis hook
    ./init_lenis.py --preset gsap --output src/scroll.js

Presets:
    vanilla - core Lenis, own RAF loop, scroll event + scrollTo helper
    gsap    - Lenis + GSAP ScrollTrigger (single ticker loop)
    react   - lenis/react ReactLenis provider and a useLenis consumer

Dependencies: Python 3 standard library only.
"""

import argparse
import sys


VANILLA = """import Lenis from 'lenis'
import 'lenis/dist/lenis.css'

const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

const lenis = new Lenis({
  duration: prefersReduced ? 0 : 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  orientation: 'vertical',
  smoothWheel: !prefersReduced,
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}
requestAnimationFrame(raf)

// Read scroll state
lenis.on('scroll', ({ scroll, velocity, progress }) => {
  document.documentElement.style.setProperty('--scroll', scroll)
  document.documentElement.style.setProperty('--scroll-progress', progress)
})

// Smooth anchor links
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault()
    lenis.scrollTo(link.getAttribute('href'))
  })
})

export { lenis }
"""


GSAP = """import Lenis from 'lenis'
import 'lenis/dist/lenis.css'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
})

// Keep ScrollTrigger in sync with Lenis
lenis.on('scroll', ScrollTrigger.update)

// Single RAF loop via GSAP's ticker; disable lag smoothing for accurate scrub
gsap.ticker.add((time) => lenis.raf(time * 1000))
gsap.ticker.lagSmoothing(0)

// Example scrubbed animation
gsap.to('.panel', {
  xPercent: -100,
  ease: 'none',
  scrollTrigger: {
    trigger: '.panel',
    start: 'top top',
    end: '+=1000',
    scrub: true,
    pin: true,
  },
})

export { lenis }
"""


REACT = """import { ReactLenis, useLenis } from 'lenis/react'

// Wrap your app once. `root` mounts Lenis on <html>.
export function SmoothScrollProvider({ children }) {
  return (
    <ReactLenis root options={{ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) }}>
      {children}
    </ReactLenis>
  )
}

// Consume the instance anywhere below the provider
export function ScrollToButton({ target, children }) {
  const lenis = useLenis()
  return (
    <button onClick={() => lenis?.scrollTo(target)}>
      {children}
    </button>
  )
}

// Subscribe to scroll
export function useScrollProgress(onProgress) {
  useLenis(({ progress }) => onProgress(progress))
}
"""


PRESETS = {'vanilla': VANILLA, 'gsap': GSAP, 'react': REACT}


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate Lenis boilerplate.')
    parser.add_argument('--preset', choices=sorted(PRESETS), help='Boilerplate preset')
    parser.add_argument('--output', help='Write to file instead of stdout')
    args = parser.parse_args()

    preset = args.preset
    if not preset:
        print('Available presets: ' + ', '.join(sorted(PRESETS)))
        try:
            preset = input('Choose preset [vanilla]: ').strip() or 'vanilla'
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        if preset not in PRESETS:
            print(f"Error: unknown preset '{preset}'", file=sys.stderr)
            return 1

    code = PRESETS[preset]

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(code)
            print(f'Wrote {preset} boilerplate to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(code)
    return 0


if __name__ == '__main__':
    sys.exit(main())
