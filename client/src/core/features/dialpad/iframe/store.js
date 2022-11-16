import logger from 'logger'

var client

export default {
  namespaced: true,

  state () {
    return {
      call: null,
      contact: null,
      user: null,
      settings: __OAUTH_APP_SETTINGS__,
    }
  },

  getters: {
    call: (state) => state.call,
    callState: (state) => state.call?.state,
    client: () => client,
    contact: (state) => state.contact,
    user: (state) => state.user,
    settings: (state) => state.settings,
  },
  
  mutations: {
    setCall(state, call) {
      state.call = call
    },

    setContact(state, contact) {
      state.contact = contact
    },

    setUser(state, user) {
      state.user = user
    },

    setSettings(state, settings) {
      state.settings = settings
    },

  },

  actions: {
    setCall ({ commit }, call) {
      logger.info('Call state changed', call)
      this.$store.commit('setCall', call);
    },

    setClient(_, dialpadClient) {
      client = dialpadClient
    },

    async setContact({ commit }, contact) {
      commit('setContact', contact)
    },

    async setUser({ commit }, user) {
      commit('setUser', user)
    },

    async setSettings({ commit }, settings) {
      commit('setSettings', settings)
    },

  },
};
