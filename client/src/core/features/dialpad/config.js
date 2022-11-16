const FEATURES = [
  {
    name: 'iframe',
    enabled:
      process.env.ENABLE_DIALPAD_IFRAME
      ? parseInt(process.env.ENABLE_DIALPAD_IFRAME)
      : 1,
  },
  {
    name: 'api',
    enabled: process.env.ENABLE_DIALPAD_API
      ? parseInt(process.env.ENABLE_DIALPAD_API)
      : 1,
  }
]

export default {
  FEATURES,
}
