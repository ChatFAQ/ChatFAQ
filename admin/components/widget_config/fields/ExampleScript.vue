<template>
    <div v-if="props.editing" class="example-script">
        {{ example }}
    </div>
    <div class="info-text" v-else>
        {{ $t("savewidgettoseeexample") }}
    </div>
</template>

<script setup>
const props = defineProps([
    "widgetConfigId", "editing"
]);
import { useItemsStore } from "~/store/items.js";
const conf = useRuntimeConfig()

const itemsStore = useItemsStore()

const example = ref(`
<div id="chatfaq-widget"></div>

<script type="module">
    import { ChatfaqWidget } from 'https://unpkg.com/chatfaq-widget@${conf.public.widgetVersion}/dist/chatfaq-widget.umd.js';

    const config = {
        element: "#chatfaq-widget",
        chatfaqApi: "<HTTP_YOUR_CHATFAQ_HOST>",
        widgetConfigId: "${props.editing}"
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
 .info-text {
     font-size: 14px;
     font-style: italic;
     color: #424242;
 }
</style>
