import { useClient } from '../client'


export default async function ({ app, store, router, feature, application }) {
  const client = useClient()
  const settings = await client.getSettings()
  await store.dispatch('dialpad/iframe/setSettings', settings)
}
