import { getProject, types } from '@theatre/core'
import studio from '@theatre/studio'

// DESIGN: Staggered reveal — a list/grid of items animates in one after another.
// Markup expected: <ul class="grid"><li>…</li> … </ul>
if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {
  studio.initialize()
}

const sheet = getProject('Stagger').sheet('Main')

const items = Array.from(document.querySelectorAll('.grid > *'))

// One sheet object per item lets each be keyframed independently in Studio.
// Offset each item's start to create the stagger.
items.forEach((el, i) => {
  const obj = sheet.object(`Item ${i + 1}`, {
    y: types.number(30, { range: [-120, 120] }),
    opacity: types.number(0, { range: [0, 1] }),
    scale: types.number(0.9, { range: [0, 1.4] }),
  })
  obj.onValuesChange(({ y, opacity, scale }) => {
    el.style.transform = `translateY(${y}px) scale(${scale})`
    el.style.opacity = opacity
  })
})

// Author per-item offsets in Studio for the staggered cascade, then play.
sheet.sequence.play({ range: [0, 2] })
