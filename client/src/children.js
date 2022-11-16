import { Feature } from '@src/vue'


const dialpad = new Feature({
  packageName: 'core/features/dialpad',
})

const bullhorn = new Feature({
  name: 'bullhorn',
  injectTo: 'dialpad/iframe/external',
})


export default {
  dialpad,
  bullhorn,
}
