<template>
    <Suspense>
        <div class="chatfaq-widget">
            <div v-if="opened" class="widget-wrapper">
                <Header class="header"/>
                <Chat class="chat"/>
                <Footer class="footer"/>
            </div>
            <div class="widget-open-button" @click="opened = !opened"><i :class="opened ? 'close' : 'open'"/></div>
        </div>
    </Suspense>
</template>

<script setup>
import Chat from "~/components/Chat.vue";
import {useGlobalStore} from "~/store";
import {ref, defineProps} from "vue";

const opened = ref();
const store = useGlobalStore();

const props = defineProps(["chatfaqWs", "chatfaqApi", "fsmDef", "title", "subtitle"]);

store.chatfaqWS = props.chatfaqWs;
store.chatfaqAPI = props.chatfaqApi;
store.fsmDef = props.fsmDef;
store.title = props.title;
store.subtitle = props.subtitle;

</script>

<style lang="scss">
@import 'assets/styles/global.scss';
</style>

<style lang="scss" scoped>
@import "../assets/styles/variables";

$widget-open-button-margin: 24px;

.widget-wrapper {
    width: 400px;
    height: 580px;
    position: absolute;
    display: flex;
    align-items: stretch;
    flex-flow: column;
    bottom: calc($chatfaq-bubble-button-size + $widget-open-button-margin);
    right: 0px;
    margin: 16px;
}


.widget-wrapper > .header {
    border: 2px solid $chatfaq-color-primary-500;
    border-radius: 10px 10px 0px 0px;
}
.widget-wrapper > .chat {
    position: relative;
    height: 100%;
    border-left: 2px solid $chatfaq-color-primary-500;
    border-right: 2px solid $chatfaq-color-primary-500;
}
.widget-wrapper > .footer {
    border: 2px solid $chatfaq-color-primary-500;
    border-radius: 0px 0px 10px 10px;
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
            content: $chatfaq-bubble-button-open-icon;
        }

        &.close {
            content: $chatfaq-bubble-button-close-icon;
        }
    }
}
</style>

