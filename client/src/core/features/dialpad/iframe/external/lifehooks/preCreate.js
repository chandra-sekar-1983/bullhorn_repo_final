import ExternalClient from '../client'


export default async function ({ feature, application }) {
  feature.context['client'] = new ExternalClient()
  feature.context['connection'] = await feature.context.client.getConnection()
};
