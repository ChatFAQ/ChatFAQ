<template>
    <Suspense>
        <div v-if="opened" class="widget-wrapper">
            <div class="widget-wrapper-header" @click="opened = false"></div>
            <Widget class="widget" />
        </div>
        <div v-else class="widget-open-button" @click="opened = true"></div>
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

.widget-wrapper {
    border: solid 1px;
    border-radius: 5px;
    border-color: #FF8E93;
    width: 300px;
    height: 450px;
    position: absolute;
    display: flex;
    align-items: stretch;
    flex-flow: column;
    bottom: 0px;
    right: 0px;
    margin: 25px;
}

.widget-wrapper-header {
    cursor: pointer;
    background-color: #FF8E93;
    height: 50px;
}

.widget-wrapper > .widget {
    position: relative;
    height: 100%;
}

.widget-open-button {
    cursor: pointer;
    background-color: #FF8E93;
    width: 50px;
    height: 50px;
    border-radius: 50px;
    position: absolute;
    bottom: 0px;
    right: 0px;
    margin: 25px;
}
</style>

