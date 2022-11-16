import { createApp } from 'vue'

import { createStore } from 'vuex';
import { createWebHistory, createRouter } from 'vue-router';

import App from '@src/App.vue'
import logger from 'logger'
import { SentryClient } from '@src/core/sentry.js'


const REQUIRED_PACKAGES = []


class Feature {
  name
  uniqueName
  parent
  children
  application
  store
  route
  context
  #packagePath
  #packageName
  #component
  #injectTo
  #urlPrefix
  #navigationGuards
  
  constructor({
    name = null,
    packagePath = null,
    packageName = null,
    parent = null,
    context = {},
    component = 'Feature.vue',
    injectTo = null,
    urlPrefix = null,
    navigationGuards = {},
    children = null,
  }) {
    this.name = name 
    this.#packageName = packageName
    this.#packagePath = packagePath
    this.parent = parent
    this.context = context
    this.#component = component
    this.#injectTo = injectTo
    this.#urlPrefix = urlPrefix
    this.#navigationGuards = navigationGuards
    this.children = children
    this.application = null
    this.store = null
    this.route = null
    this.uniqueName = null
    return this
  }

  get json() {
    return {
      name: this.name,
      uniqueName: this.uniqueName,
      packageName: this.#packageName,
      packagePath: this.#packagePath,
      parent: this.parent?.uniqueName,
      context: this.context,
      injectTo: this.#injectTo,
      urlPrefix: this.#urlPrefix,
      store: this.store,
      route: this.route,
    }
  }

  get urlPrefix() {
    return this.#urlPrefix
  }

  get fullUrl() {
    if (this.parent) {
      return `${this.parent.fullUrl}/${this.urlPrefix}`
    }
    return ''
  }

  get isRoot() {
    return this.parent === null
  }

  async load(parent, application) {
    this.parent = parent
    this.application = application
    if (this.#packageName) {
      this.name = this.#packageName.split('/').pop()
      this.#packagePath = `./${this.#packageName}`
    } else {
      this.#packageName = this.name
    }

    this.#packagePath = this.#packagePath || `${this.parent.#packagePath}/${this.#packageName}`
    if (this.#injectTo) {
      delete this.parent.children[this.name]
      this.parent = this.application.getFeature(`${root.uniqueName}/${this.#injectTo}`)
      if (!this.parent) {
        throw new Error(`Cannot inject to (${this.#injectTo}), it does not exists`)
      }
    }

    this.#urlPrefix = this.#urlPrefix || `${this.name}`
    this.uniqueName = this.isRoot ? this.name : `${this.parent.uniqueName}/${this.name}`
    this.children = await this.#importChildren()

    logger.debug(`Feature created: ${JSON.stringify(this.json)}`)
    return this
  }

  addChild(feature) {
    this.children[feature.name] = feature
  }

  async initialize() {
    logger.debug(`Initializing feature: ${JSON.stringify(this.json)}`)

    await this.#importInit()
    this.config = await this.#importConfig()
    var storeModules = {}
    var featureRoutes = [] 
    for (var [name, feature] of Object.entries(this.children)) {
      if (!window.location.pathname.startsWith(feature.fullUrl)) {
        continue
      }

      feature = await feature.initialize()
      if (
        feature.route &&
        Object.keys(feature.route).length !== 0 &&
        Object.getPrototypeOf(feature.route) === Object.prototype
      ) {
        featureRoutes.push(feature.route)
      }
      if (feature.store) {
        storeModules[feature.name] = feature.store
      }
    }

    this.route = await this.#getRoute(featureRoutes)
    this.store = await this.#getStore(storeModules)
    logger.debug(`Initialized feature: ${JSON.stringify(this.json)}`)
    return this
  }

  async #importChildPackage(packageName) {
    try {
      let _module = await import(`${this.#packagePath}/${packageName}`)
      return _module.default
    } catch (e) {
      if (packageName in REQUIRED_PACKAGES || e.code !== 'MODULE_NOT_FOUND') {
        throw new Error(`
          Something went wrong importing required module: ${this.#packagePath}/${packageName} \n
          ${e}
        `)
      }
    }
  }

  async #importChildren() {
    return await this.#importChildPackage('children') || {}
  }

  async #importInit() {
    return await this.#importChildPackage('lifehooks/init')
  }

  async #importConfig() {
    return await this.#importChildPackage('config')
  }

  async #getStore(storeModules) {
    const store = await this.#importChildPackage('store')
    if (store === undefined && Object.keys(storeModules).length === 0) {
      return
    }
    return {
      namespaced: true,
      ...store,
      ...Object.keys(storeModules).length > 0 ? { modules: storeModules } : {}
    }
  }

  async #importComponent() {
    return await this.#importChildPackage(`${this.#component}`)
  }

  async #importPostCreate() {
    return await this.#importChildPackage('lifehooks/postCreate')
  }

  async #importPreCreate() {
    return await this.#importChildPackage('lifehooks/preCreate')
  }

  async #getRoute(featureRoutes) {
    let component = await this.#importComponent()
    this.routes = await this.#importChildPackage('routes') || []

    if (featureRoutes.length === 0 && this.routes.length === 0 && component === undefined) {
      return
    }

    if ((featureRoutes.length > 0 || this.routes.length > 0) && component === undefined) {
      throw new Error(`
        Feature ${this.name}:
          Component Feature.vue has to be defined with <router-view /> component.
      `)
    }

    const routes = featureRoutes.concat(this.routes)

    return {
      name: this.name,
      path: this.#urlPrefix,
      component: component,
      ...this.#navigationGuards,
      ...(routes?.length > 0 ? { children: routes } : {}),
    }
  }

  async preCreate({ application }) {
    const preCreateFunc = await this.#importPreCreate()
    if (preCreateFunc) {
      await preCreateFunc({ feature: this, application })
    }

    for (var [name, feature] of Object.entries(this.children)) {
      if (!window.location.pathname.startsWith(feature.fullUrl)) {
        continue
      }
      await feature.preCreate({ application })
    }
  }

  async postCreate({ app, store, router, application }) {
    const postCreateFunc = await this.#importPostCreate()
    if (postCreateFunc) {
      await postCreateFunc({ app, store, router, feature: this, application: application })
    }

    for (var [name, feature] of Object.entries(this.children)) {
      if (!window.location.pathname.startsWith(feature.fullUrl)) {
        continue
      }
      await feature.postCreate({ app, store, router, application })
    }
  }
}

const root = new Feature({ name: 'dpi', packagePath: '.', urlPrefix: '/' })

class Application {
  #featureTree;

  constructor() {
    this.#featureTree = {}
  }

  setFeature(feature) {
    this.#featureTree[feature.uniqueName] = feature
  }

  getFeature(featureName) {
    return featureName in this.#featureTree ? this.#featureTree[featureName] : null
  }

  async #createFeatureTree(feature, parent=null) {
    feature = await feature.load(parent, this)

    this.setFeature(feature)
    if (feature.parent) {
      feature.parent.addChild(feature)
    }

    for (var [name, child] of Object.entries(feature.children)) {
      await this.#createFeatureTree(child, parent=feature)
    }
  }

  #configureVue() {
    this.vueApp = createApp(App)
    // Dummy i18n
    this.vueApp.config.globalProperties.$i18n = function (text, data) {
      if (data === undefined || data === null) {
        return text;
      }
      let finalString = text;
      if (data) {
        Object.keys(data).forEach((key) => {
          finalString = finalString.replace(`[${key}]`, data[key]);
        });
      }
      return finalString;
    };

    this.vueApp.config.globalProperties.$logger = logger
    this.vueApp.config.globalProperties.$application = this

    this.store = createStore(this.root.store)
    this.vueApp.use(this.store);

    this.router = createRouter({
      history: createWebHistory(),
      routes: [this.root.route],
    })
    this.vueApp.use(this.router);
  }

  #setInterceptors() {
    const { fetch: originalFetch } = window;

    window.fetch = async (...args) => {
      let [resource, config ] = args;
      let fetchResponse;
      // request interceptor here
      if (config.setLoading)
        await this.store.dispatch('setLoading', true)
      try {
        fetchResponse = await originalFetch(resource, config);
      } catch (e) {
        logger.info(`Request returned with not ok status: ${e}`);
      }
      if (config.setLoading)
        await this.store.dispatch('setLoading', false)
      // response interceptor here
      return fetchResponse;
    }
  }

  async initializeThirdParty() {
    new SentryClient(this.vueApp, this.router);
  }

  async create() {
    await this.#createFeatureTree(root)
    this.root = this.getFeature(root.name)

    await this.root.initialize()
    await this.root.preCreate({ application: this })
    this.#configureVue()
    this.#setInterceptors()
    await this.root.postCreate({
      app: this.vueApp,
      store: this.store,
      router: this.router,
      application: this
    })
    this.vueApp.mount('#app');
    await this.initializeThirdParty();
    return this
  }
}

export {
  Feature,
  Application,
}
