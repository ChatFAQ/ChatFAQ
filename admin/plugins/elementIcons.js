import * as ElementPlusIconsVue from '@element-plus/icons-vue'

export default defineNuxtPlugin(({ vueApp }) => {
    for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
      vueApp.component(key, component)
    }
});
