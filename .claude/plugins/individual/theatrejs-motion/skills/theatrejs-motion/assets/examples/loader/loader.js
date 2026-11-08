import { getProject, types } from '@theatre/core'
import studio from '@theatre/studio'

// DESIGN: Looping loader — a progress ring sweeps and a label pulses.
// Markup expected: <div class="loader"><svg>…<circle class="ring"/></svg>
//   <span class="loader-label">Loading</span></div>
if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {
  studio.initialize()
}

const sheet = getProject('Loader').sheet('Main')

const ring = document.querySelector('.ring')
const label = document.querySelector('.loader-label')

// Set the SVG circle up for dash animation (circumference ~= 2 * PI * r)
const CIRCUMFERENCE = 283 // r = 45
if (ring) {
  ring.style.strokeDasharray = String(CIRCUMFERENCE)
}

const loaderObj = sheet.object('Loader', {
  progress: types.number(0, { range: [0, 1] }),   // 0 -> 1 sweep
  spin: types.number(0, { range: [0, 360] }),      // rotation
  labelOpacity: types.number(1, { range: [0, 1] }),
})

loaderObj.onValuesChange(({ progress, spin, labelOpacity }) => {
  if (ring) {
    ring.style.strokeDashoffset = String(CIRCUMFERENCE * (1 - progress))
    ring.style.transform = `rotate(${spin}deg)`
    ring.style.transformOrigin = '50% 50%'
  }
  if (label) label.style.opacity = labelOpacity
})

// Loop forever while loading; stop with sheet.sequence.pause() when ready.
sheet.sequence.play({ iterationCount: Infinity, range: [0, 1.2] })
