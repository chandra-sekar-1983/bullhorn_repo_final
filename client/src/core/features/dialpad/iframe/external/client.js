import logger from 'logger';
import { useRequests } from 'requests'

const { makeGET } = useRequests({ postFix: '/dialpad/iframe/external' })


class ExternalClient {

  async getConnection () {
    return await makeGET('/connection')
  }
}

export default ExternalClient;
