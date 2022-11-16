import config from 'config'
import logger from 'logger'


export const useRequests = (options = {}) => {
  const baseUrl = `${options.baseUrl || config.BASE_URL}${options.postFix || ''}`

  const makeRequest = async (uri, options = {}) => {
    const data = options.data || {}
    const opts = {
      method: options.method || 'GET',
      headers: options.headers || {},
      setLoading: options.setLoading !== undefined ? options.setLoading : true,
      ...Object.keys(data).length !== 0 ? { body: JSON.stringify(data) } : {},
    }
    const params = new URLSearchParams({
      access_token: __ACCESS_TOKEN__,
      ...(options.params || {}),
    })
    const url = new URL(`${baseUrl}${uri}?${params.toString()}`)

    try {
      const res = await fetch(url, opts)
      if (res.status !== 204 && res.ok) {
        return await res.json()
      }
    } catch (e) {
      logger.info(`Request ${method} to ${url} returned with not ok status: ${e}`);
    }
  }

  const makeGET = async (uri, options={}) => {
    return await makeRequest(uri, { method: 'GET', ...options })
  }

  const makePOST = async (uri, options={}) => {
    return await makeRequest(uri, { method: 'POST', ...options })
  }

  const makePUT = async (uri, options={}) => {
    return await makeRequest(uri, { method: 'PUT', ...options })
  }

  const makePATCH = async (uri, options={}) => {
    return await makeRequest(uri, { method: 'PATCH', ...options })
  }

  const makeDELETE = async (uri, options={}) => {
    return await makeRequest(uri, { method: 'DELETE', ...options })
  }

  return {
    makeGET,
    makePOST,
    makePUT,
    makePATCH,
    makeDELETE,
    makeRequest,
  }
}
