export default async function ({ app, store, router, feature, application }) {
  await store.dispatch('dialpad/iframe/external/setClient', feature.context['client'])
  await store.dispatch(
    'dialpad/iframe/external/setConnection',
    feature.context['connection']
  )
};
