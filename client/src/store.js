export default {
  state () {
    return {
      user: null,
      error: null,
      loading: false,
    };
  },

  getters: {
    loading: (state) => state.loading,
    user: (state) => state.user,
    hasError (state) {
      return state.error
    },
  },

  mutations: {
    setUser (state, val) {
      state.user = val
    },

    setError (state, val) {
      state.error = val
    },

    setLoading (state, val) {
      state.loading = val
    },
  },

  actions: {
    setUser ({ commit }, val) {
      commit('setUser', val)
    },

    setError ({ commit }, val) {
      commit('setError', val)
    },

    async setLoading ({ commit }, val) {
      commit('setLoading', val)
    },
  },
}
