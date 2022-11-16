import * as Sentry from "@sentry/vue";

import config from 'config';

const TRACE = 'TRACE'
const DEBUG = 'DEBUG'
const WARNING = 'WARNING'
const INFO = 'INFO'
const ERROR = 'ERROR'
const CRITICAL = 'CRITICAL'

const LEVELS = {
  TRACE: 1,
  DEBUG: 2,
  WARNING: 3,
  INFO: 4,
  ERROR: 5,
  CRITICAL: 6,
}

const LEVEL = process.env.LOGGING_LEVEL ? process.env.LOGGING_LEVEL : TRACE

const isEnabled = (level) => {
  return LEVELS[level] >= LEVELS[LEVEL]
}

const formatMessage = (message) => {
  return `${config.NAME}: ${message}`
}

const processMessage = (message) => {
  const msg = formatMessage(message);
  Sentry.captureMessage(msg)
  return msg
}

const trace = (message) => {
  if(isEnabled(TRACE)) {
    console.log(processMessage(message))
  }
};

const debug = (message) => {
  if(isEnabled(DEBUG)) {
    console.log(processMessage(message))
  }
};

const warning = (message) => {
  if(isEnabled(WARNING)) {
    console.warn(processMessage(message))
  }
};

const info = (message) => {
  if (isEnabled(INFO)) {
    console.log(processMessage(message))
  }
};

const error = (message) => {
  if (isEnabled(ERROR)) {
    console.error(processMessage(message))
  }
};

export default {
  trace,
  debug,
  warning,
  info,
  error,
}
