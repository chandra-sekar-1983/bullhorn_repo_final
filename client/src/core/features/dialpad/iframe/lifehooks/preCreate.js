import logger from 'logger'
import DialpadClient from '../core/dialpad_client'


export default async function ({ feature, application }) {
  const dialpadClient = new DialpadClient({
    schedulerType: 'queue',
  })
  await dialpadClient.init()
  feature.context['client'] = dialpadClient
}
