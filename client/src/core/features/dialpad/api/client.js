// A client to consume /dialpad/api endpoints

import { useRequests } from 'requests'

const { makeGET } = useRequests({ postFix: '/dialpad/api' })

export const useClient = () => {

  
  const getSettings = async () => {
    return await makeGET('/settings')
  }

  return {
    getSettings,
  }
}
