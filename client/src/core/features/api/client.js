// A client to consume /api endpoints

import { useRequests } from 'requests'

const { makeGET } = useRequests({ postFix: '/api' })

export const useClient = () => {

  const getUser = async (userId) => {
    return await makeGET(`/user/${userId}`)
  }

  return {
    getUser,
  }

}
