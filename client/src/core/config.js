const NAME = process.env.NAME || 'dpi'
const ENV = process.env.ENV || 'dev'
const DEBUG = process.env.DEBUG ? parseInt(process.env.DEBUG) : 0
const BASE_URL = process.env.BASE_URL || ''

const isDev = ENV === 'dev'
const isBeta = ENV === 'beta'
const isProduction = ENV === 'production'
const isDebug = isDev || DEBUG
const isRemoteLocalhost = process.env.REMOTE_LOCALHOST ? parseInt(process.env.REMOTE_LOCALHOST) : 0

export default {
  ENV,
  NAME,
  DEBUG,
  BASE_URL,
  isDev,
  isBeta,
  isProduction,
  isDebug,
  isRemoteLocalhost,
};
