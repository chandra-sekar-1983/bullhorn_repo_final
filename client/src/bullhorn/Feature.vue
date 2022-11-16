<template>
  BULLHORN
  <div>
  SETTINGS: {{ $store.getters['dialpad/iframe/settings'] }}
  </div>
  <dt-button @click="$router.push({ name: 'matches' })">GO</dt-button>
  <router-view></router-view>
</template>
<script setup>
import { DtButton } from '@dialpad/dialtone-vue';
console.log('Feature.vue')
</script>
