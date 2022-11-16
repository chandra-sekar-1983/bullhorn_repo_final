<template>
  <transition name="fade">
    <div v-show="isErrorOnDisplay">
      <app-error>{{ $store.getters.error }}</app-error>
    </div>
  </transition>
  <transition name="fade">
    <div v-show="isLoadingOnDisplay">
      <loading />
    </div>
  </transition>
  <transition name="fade">
    <div v-show="isFeatureOnDisplay">
      <router-view />
    </div>
  </transition>
</template>

<script setup>
import { onErrorCaptured, computed } from 'vue'
import { useStore } from 'vuex'

import AppError from '@components/AppError.vue'
import Loading from '@components/Loading.vue'

const store = useStore()
onErrorCaptured((err) => {
  store.dispatch('setError', `Upps! Something went wrong! {err}`)
});

const isErrorOnDisplay = computed(() => store.getters.error)
const isLoadingOnDisplay = computed(() => !isErrorOnDisplay.value && store.getters.loading)
const isFeatureOnDisplay = computed(() => !isErrorOnDisplay.value && !isLoadingOnDisplay.value)
</script>

<style lang="less">
@import "@dialpad/dialtone/build/less/dialtone.less";

.hcf-layout {
  display: grid;
  min-height: 98%;
  grid-template-areas: "header" "content" "footer";
  grid-template-rows: auto 1fr auto;
  grid-gap: 6px;
  grid-template-columns: 100%;
  margin-top: 6px;
  .d-fs14();

  &__header {
    grid-area: header;
    padding: 2px;
  }

  &__content {
    grid-area: content;
    padding: 2px;
  }

  &__footer {
    grid-area: footer;
    padding: 2px;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
