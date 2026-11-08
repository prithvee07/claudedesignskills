import { getProject, types } from '@theatre/core'
import studio from '@theatre/studio'

// DESIGN: Hero intro — headline and subtitle rise and fade in, staggered.
// Markup expected: <h1 class="headline">…</h1><p class="subtitle">…</p>
if (import.meta.env?.DEV ?? process.env.NODE_ENV !== 'production') {
  studio.initialize()
}

const sheet = getProject('Hero Intro').sheet('Intro')

const headline = document.querySelector('.headline')
const subtitle = document.querySelector('.subtitle')

const headlineObj = sheet.object('Headline', {
  y: types.number(60, { range: [-200, 200] }),
  opacity: types.number(0, { range: [0, 1] }),
  blur: types.number(12, { range: [0, 40] }),
})

const subtitleObj = sheet.object('Subtitle', {
  y: types.number(40, { range: [-200, 200] }),
  opacity: types.number(0, { range: [0, 1] }),
})

headlineObj.onValuesChange(({ y, opacity, blur }) => {
  headline.style.transform = `translateY(${y}px)`
  headline.style.opacity = opacity
  headline.style.filter = `blur(${blur}px)`
})

subtitleObj.onValuesChange(({ y, opacity }) => {
  subtitle.style.transform = `translateY(${y}px)`
  subtitle.style.opacity = opacity
})

// Author the stagger in Studio (e.g. subtitle starts ~0.3s after headline),
// then play the intro once.
sheet.sequence.play({ range: [0, 1.6] })
