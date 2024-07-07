import Highlight from '/home/bober/Desktop/money/safeRidesAB/frontend/node_modules/@nuxtjs/mdc/dist/runtime/shiki/index.mjs'

export const remarkPlugins = {
}

export const rehypePlugins = {
  'highlight': { instance: Highlight, options: {"src":"/home/bober/Desktop/money/safeRidesAB/frontend/node_modules/@nuxtjs/mdc/dist/runtime/shiki/index.mjs"} },
}

export const highlight = {"theme":"github-dark"}