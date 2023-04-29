import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import vuetify from './plugins/vuetify'

import VueHighlightJS from 'vue-highlightjs'
import "highlight.js/styles/dark.css";
Vue.use(VueHighlightJS)


import {Chart} from 'chart.js'
import Chartkick from 'vue-chartkick'
Vue.use(Chartkick.use(Chart));


Vue.config.productionTip = false

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

Vue.prototype.$axios = axios