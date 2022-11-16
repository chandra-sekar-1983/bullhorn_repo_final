var _externalClient


export default {
  namespaced: true,
  state () {
    return {
      connection: null,
    }
  },

  getters: {
    client: () => _externalClient,
    connection: (state) => state.connection,
    isConnected: (state) => state.connection?.connected,
    authUrl: (state) => state.connection?.authorization_url,
  },

  mutations: {
    setConnection (state, connection) {
      state.connection = connection
    },
  },

  actions: {
    setConnection ({ commit }, connection) {
      commit('setConnection', connection)
    },

    async setClient ({ state }, externalClient) {
      _externalClient = externalClient
    },
  }
}
