
import { updateAppConfig } from '#app/config'
import { defuFn } from 'defu'

const inlineConfig = {
  "nuxt": {
    "buildId": "dev"
  }
}

// Vite - webpack is handled directly in #app/config
if (import.meta.hot) {
  import.meta.hot.accept((newModule) => {
    updateAppConfig(newModule.default)
  })
}

import cfg0 from "/home/bober/Desktop/money/safeRidesAB/frontend/app/app.config.ts"
import cfg1 from "/home/bober/Desktop/money/safeRidesAB/frontend/app.config.ts"

export default /*@__PURE__*/ defuFn(cfg0, cfg1, inlineConfig)
