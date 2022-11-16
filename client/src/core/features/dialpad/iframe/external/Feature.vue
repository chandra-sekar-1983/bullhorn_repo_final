<template>
  <router-view v-if="isConnected" />
  <connect v-else />
</template>

<script setup>
import { mapGetters } from 'vuex'
import Connect from './components/Connect.vue'
</script>

<script>
export default {
  computed: {
    ...mapGetters({
      isConnected: 'dialpad/iframe/external/isConnected',
    })
  }
}
</script>
