 export default {
  namespaced: true,
  state () {
    return {
      name: 'Bullhorn',
    }
  },

  getters: {
    intname: (state) => state.name 
  },

  mutations: {},

  actions: {},
}
