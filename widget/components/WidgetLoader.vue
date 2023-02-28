<template>
    <Suspense>
        <div class="chatfaq-widget">
            <div v-if="opened" class="widget-wrapper">
                <div class="widget-wrapper-header" @click="opened = false"></div>
                <Widget class="widget" />
            </div>
            <div class="widget-open-button" @click="opened = !opened"><i :class="opened ? 'close' : 'open'" /></div>
        </div>
    </Suspense>
</template>

<script setup>
import Widget from "~/components/Widget.vue";
import { useGlobalStore } from "~/store";
import { ref, defineProps } from "vue";

const opened = ref();
const store = useGlobalStore();

const props = defineProps(["chatfaqWs", "chatfaqApi"]);

store.chatfaqWS = props.chatfaqWs;
store.chatfaqAPI = props.chatfaqApi;

</script>

<style lang="scss">
@import 'assets/styles/global.scss';
@import 'primevue/resources/themes/saga-blue/theme.css';
@import 'primevue/resources/primevue.css';
@import 'primeicons/primeicons.css';
@import 'primeflex/primeflex.css';
</style>

<style lang="scss" scoped>
@import "../assets/styles/variables";

$widget-open-button-margin: 24px;

.widget-wrapper {
    border: solid 1px;
    border-radius: 5px;
    border-color: $chatfaq-main-color;
    width: 300px;
    height: 450px;
    position: absolute;
    display: flex;
    align-items: stretch;
    flex-flow: column;
    bottom: calc($chatfaq-bubble-button-size + $widget-open-button-margin);
    right: 0px;
    margin: 16px;
}

.widget-wrapper-header {
    cursor: pointer;
    background-color: $chatfaq-main-color;
    height: 50px;
}

.widget-wrapper > .widget {
    position: relative;
    height: 100%;
}

.widget-open-button {
    cursor: pointer;
    background: $chatfaq-color-gradient-pink;
    width: $chatfaq-bubble-button-size;
    height: $chatfaq-bubble-button-size;
    border-radius: $chatfaq-bubble-button-size;
    position: absolute;
    bottom: 0px;
    right: 0px;
    margin: $widget-open-button-margin;
    i {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        &.open {
            content: $chatfaq-bubble-button-open;
        }
        &.close {
            content: $chatfaq-bubble-button-close;
        }
    }
}
</style>

