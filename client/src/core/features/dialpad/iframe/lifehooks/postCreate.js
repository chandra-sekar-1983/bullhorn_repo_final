import logger from 'logger'


export default async function ({ app, store, router, feature, application }) {
  const dialpadClient = feature.context['client']
  await store.dispatch('dialpad/iframe/setClient', dialpadClient)
  // Get dialpad contact data as soon as possible.
  const currentContact = await dialpadClient.getCurrentContact()
  await store.dispatch('dialpad/iframe/setContact', currentContact);

  // Get the current dialpad user accessing this app.
  const currentUser = await dialpadClient.getCurrentUser()
  await store.dispatch('dialpad/iframe/setUser', currentUser);
  await store.dispatch('setUser', { id: currentUser.id })

}
