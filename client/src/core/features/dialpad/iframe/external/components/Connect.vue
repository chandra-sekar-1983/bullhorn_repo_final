<template>
  <div>
    {{ $i18n('Connect to') }}
    <dt-link @click="authorize" href="#">{{ config.NAME }}</dt-link>
  </div>
</template>

<script setup>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

import config from 'config';
import { DtLink } from '@dialpad/dialtone-vue';

import Connect from '../components/Connect.vue'

const store = useStore()
const router = useRouter()
const dialpadClient = store.getters['dialpad/iframe/client']
const externalClient = store.getters['dialpad/iframe/external/client']

const authCallback = async () => {
  store.dispatch(
    'dialpad/iframe/external/setConnection', await externalClient.getConnection()
  )
}

const authorize = () => {
  dialpadClient.auth(
    authCallback,
    { url: store.getters['dialpad/iframe/external/authUrl'], service: config.NAME } 
  )
}
</script>
