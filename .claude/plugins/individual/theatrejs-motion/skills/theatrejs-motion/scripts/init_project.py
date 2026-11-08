#!/usr/bin/env python3
"""
Theatre.js Project Boilerplate Generator

Generates ready-to-edit Theatre.js setup code for one of three presets.
Studio is always guarded behind a dev check so it never ships to production.

Usage:
    ./init_project.py                       # interactive mode
    ./init_project.py --preset vanilla      # DOM/vanilla JS setup
    ./init_project.py --preset r3f          # React Three Fiber setup
    ./init_project.py --preset scroll       # scroll-driven sequence setup
    ./init_project.py --preset r3f --project "My Demo" --sheet Scene

Presets:
    vanilla  - @theatre/core + studio, animates a DOM element
    r3f      - @theatre/r3f with SheetProvider + editable mesh/camera
    scroll   - scroll position mapped onto the sequence
    hero     - staggered hero headline + subtitle intro reveal
    loader   - looping loader / progress ring
    stagger  - staggered list/grid item reveal

Dependencies: Python 3 standard library only.
"""

import argparse
import sys


def vanilla(project: str, sheet: str) -> str:
    return f'''import {{ getProject, types }} from '@theatre/core'
import studio from '@theatre/studio'

// Studio is dev-only — guard it out of production
if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {{
  studio.initialize()
}}

const project = getProject('{project}')
const sheet = project.sheet('{sheet}')

const box = document.querySelector('.box')

const boxObj = sheet.object('Box', {{
  x: types.number(0, {{ range: [-300, 300] }}),
  y: types.number(0, {{ range: [-300, 300] }}),
  opacity: types.number(1, {{ range: [0, 1] }}),
  rotation: types.number(0, {{ range: [-180, 180] }}),
}})

boxObj.onValuesChange(({{ x, y, opacity, rotation }}) => {{
  box.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{rotation}}deg)`
  box.style.opacity = opacity
}})

// Author keyframes in Studio, then play:
sheet.sequence.play({{ iterationCount: Infinity, range: [0, 3] }})
'''


def r3f(project: str, sheet: str) -> str:
    return f'''import {{ Canvas }} from '@react-three/fiber'
import {{ useEffect }} from 'react'
import {{ getProject }} from '@theatre/core'
import {{ SheetProvider, editable as e, PerspectiveCamera }} from '@theatre/r3f'
import studio from '@theatre/studio'
import extension from '@theatre/r3f/dist/extension'

if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {{
  studio.initialize()
  studio.extend(extension)
}}

const sheet = getProject('{project}').sheet('{sheet}')

function Rig() {{
  useEffect(() => {{
    sheet.sequence.play({{ iterationCount: Infinity, range: [0, 4] }})
  }}, [])
  return null
}}

export default function App() {{
  return (
    <Canvas>
      <SheetProvider sheet={{sheet}}>
        <PerspectiveCamera theatreKey="Camera" makeDefault position={{[0, 0, 6]}} />
        <ambientLight intensity={{0.6}} />
        <directionalLight position={{[5, 5, 5]}} />
        <e.mesh theatreKey="Cube">
          <boxGeometry />
          <meshStandardMaterial color="hotpink" />
        </e.mesh>
        <Rig />
      </SheetProvider>
    </Canvas>
  )
}}
'''


def scroll(project: str, sheet: str) -> str:
    return f'''import {{ getProject, types }} from '@theatre/core'
import studio from '@theatre/studio'

if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {{
  studio.initialize()
}}

const sheet = getProject('{project}').sheet('{sheet}')

const hero = document.querySelector('.hero')

const heroObj = sheet.object('Hero', {{
  y: types.number(0, {{ range: [-500, 500] }}),
  scale: types.number(1, {{ range: [0, 3] }}),
  opacity: types.number(1, {{ range: [0, 1] }}),
}})

heroObj.onValuesChange(({{ y, scale, opacity }}) => {{
  hero.style.transform = `translateY(${{y}}px) scale(${{scale}})`
  hero.style.opacity = opacity
}})

// Length (seconds) of the authored sequence — keep in sync with Studio
const SEQ_LENGTH = 5

let ticking = false
function updateFromScroll() {{
  const max = document.documentElement.scrollHeight - window.innerHeight
  const progress = max > 0 ? window.scrollY / max : 0
  sheet.sequence.position = progress * SEQ_LENGTH
  ticking = false
}}

window.addEventListener('scroll', () => {{
  if (!ticking) {{
    requestAnimationFrame(updateFromScroll)
    ticking = true
  }}
}}, {{ passive: true }})

updateFromScroll()
'''


def hero(project: str, sheet: str) -> str:
    return f'''import {{ getProject, types }} from '@theatre/core'
import studio from '@theatre/studio'

// DESIGN: Hero intro — headline and subtitle rise and fade in, staggered.
// Markup expected: <h1 class="headline">…</h1><p class="subtitle">…</p>
if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {{
  studio.initialize()
}}

const sheet = getProject('{project}').sheet('{sheet}')

const headline = document.querySelector('.headline')
const subtitle = document.querySelector('.subtitle')

const headlineObj = sheet.object('Headline', {{
  y: types.number(60, {{ range: [-200, 200] }}),
  opacity: types.number(0, {{ range: [0, 1] }}),
  blur: types.number(12, {{ range: [0, 40] }}),
}})

const subtitleObj = sheet.object('Subtitle', {{
  y: types.number(40, {{ range: [-200, 200] }}),
  opacity: types.number(0, {{ range: [0, 1] }}),
}})

headlineObj.onValuesChange(({{ y, opacity, blur }}) => {{
  headline.style.transform = `translateY(${{y}}px)`
  headline.style.opacity = opacity
  headline.style.filter = `blur(${{blur}}px)`
}})

subtitleObj.onValuesChange(({{ y, opacity }}) => {{
  subtitle.style.transform = `translateY(${{y}}px)`
  subtitle.style.opacity = opacity
}})

// Author the stagger in Studio (e.g. subtitle starts ~0.3s after headline),
// then play the intro once.
sheet.sequence.play({{ range: [0, 1.6] }})
'''


def loader(project: str, sheet: str) -> str:
    return f'''import {{ getProject, types }} from '@theatre/core'
import studio from '@theatre/studio'

// DESIGN: Looping loader — a progress ring sweeps and a label pulses.
// Markup expected: <div class="loader"><svg>…<circle class="ring"/></svg>
//   <span class="loader-label">Loading</span></div>
if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {{
  studio.initialize()
}}

const sheet = getProject('{project}').sheet('{sheet}')

const ring = document.querySelector('.ring')
const label = document.querySelector('.loader-label')

// Set the SVG circle up for dash animation (circumference ~= 2 * PI * r)
const CIRCUMFERENCE = 283 // r = 45
if (ring) {{
  ring.style.strokeDasharray = String(CIRCUMFERENCE)
}}

const loaderObj = sheet.object('Loader', {{
  progress: types.number(0, {{ range: [0, 1] }}),   // 0 -> 1 sweep
  spin: types.number(0, {{ range: [0, 360] }}),      // rotation
  labelOpacity: types.number(1, {{ range: [0, 1] }}),
}})

loaderObj.onValuesChange(({{ progress, spin, labelOpacity }}) => {{
  if (ring) {{
    ring.style.strokeDashoffset = String(CIRCUMFERENCE * (1 - progress))
    ring.style.transform = `rotate(${{spin}}deg)`
    ring.style.transformOrigin = '50% 50%'
  }}
  if (label) label.style.opacity = labelOpacity
}})

// Loop forever while loading; stop with sheet.sequence.pause() when ready.
sheet.sequence.play({{ iterationCount: Infinity, range: [0, 1.2] }})
'''


def stagger(project: str, sheet: str) -> str:
    return f'''import {{ getProject, types }} from '@theatre/core'
import studio from '@theatre/studio'

// DESIGN: Staggered reveal — a list/grid of items animates in one after another.
// Markup expected: <ul class="grid"><li>…</li> … </ul>
if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {{
  studio.initialize()
}}

const sheet = getProject('{project}').sheet('{sheet}')

const items = Array.from(document.querySelectorAll('.grid > *'))

// One sheet object per item lets each be keyframed independently in Studio.
// Offset each item's start to create the stagger.
items.forEach((el, i) => {{
  const obj = sheet.object(`Item ${{i + 1}}`, {{
    y: types.number(30, {{ range: [-120, 120] }}),
    opacity: types.number(0, {{ range: [0, 1] }}),
    scale: types.number(0.9, {{ range: [0, 1.4] }}),
  }})
  obj.onValuesChange(({{ y, opacity, scale }}) => {{
    el.style.transform = `translateY(${{y}}px) scale(${{scale}})`
    el.style.opacity = opacity
  }})
}})

// Author per-item offsets in Studio for the staggered cascade, then play.
sheet.sequence.play({{ range: [0, 2] }})
'''


PRESETS = {
    'vanilla': vanilla,
    'r3f': r3f,
    'scroll': scroll,
    'hero': hero,
    'loader': loader,
    'stagger': stagger,
}


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate Theatre.js boilerplate.')
    parser.add_argument('--preset', choices=sorted(PRESETS), help='Boilerplate preset')
    parser.add_argument('--project', default='My Project', help='Theatre.js project name')
    parser.add_argument('--sheet', default='Scene', help='Sheet name')
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

    code = PRESETS[preset](args.project, args.sheet)

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
