<template>
    <div v-if="itemsStore.editing" class="example-script">
        {{ example }}
    </div>
    <div v-else>
        Save the widget to see the example script
    </div>
</template>

<script setup>
const props = defineProps([
    "widgetConfigId"
]);
import { useItemsStore } from "~/store/items.js";

const itemsStore = useItemsStore()

const example = ref(`
<div id="chatfaq-widget"></div>

<script type="module">
    import { ChatfaqWidget } from 'https://unpkg.com/chatfaq-widget@0.0.29/dist/chatfaq-widget.mjs';

    const config = {
    element: "#chatfaq-widget",
    chatfaqApi: "<HTTP_YOUR_CHATFAQ_HOST>",
    chatfaqWs: "<WS_YOUR_CHATFAQ_HOST>",
    widgetConfigId: "${itemsStore.editing}"
  }
  const chatfaqWidget = new ChatfaqWidget(config);
  chatfaqWidget.mount()
\<\/script>
`)
</script>

<style lang="scss" scoped>
 .example-script {
        background-color: #424242;
        padding-left: 20px;
        padding-bottom: 20px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 14px;
        line-height: 1.5;
        color: white;
        white-space: pre-wrap;
 }
</style>
