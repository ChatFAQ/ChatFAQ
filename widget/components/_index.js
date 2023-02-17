import WidgetLoader from './WidgetLoader.vue';

import { createApp } from 'vue'
function loadWidget(tagId) {
    createApp(WidgetLoader).mount(tagId);
}
export { loadWidget }
