import config from 'config'


const DIALPAD_URL = process.env.DIALPAD_URL
const DIALPAD_CLIENT_ALLOWED_ORIGINS = [
  DIALPAD_URL,
  ...config.isDev || config.isRemoteLocalhost ? ['http://localhost:8087', config.BASE_URL] : [],
]

export default {
  DIALPAD_URL,
  DIALPAD_CLIENT_ALLOWED_ORIGINS,
}
