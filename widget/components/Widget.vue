<template>
    <Suspense>
        <div class="chatfaq-widget">
            <div v-if="opened" class="widget-wrapper">
                <div v-if="store.historyOpened" class="widget-history" :class="{'maximized': store.maximized}">
                </div>
                <div class="flex-column" :class="{'maximized': store.maximized}">
                    <Header class="header" :class="{'history': store.historyOpened}"/>
                    <Chat class="chat" :class="{'history': store.historyOpened}"/>
                    <Footer class="footer" :class="{'history': store.historyOpened}"/>
                </div>
            </div>
            <div class="widget-open-button" @click="opened = !opened"><i :class="opened ? 'close' : 'open'"/></div>
        </div>
    </Suspense>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import {ref, defineProps} from "vue";

const opened = ref();
const store = useGlobalStore();

const props = defineProps(["chatfaqWs", "chatfaqApi", "fsmDef", "userId", "title", "subtitle"]);

store.chatfaqWS = props.chatfaqWs;
store.chatfaqAPI = props.chatfaqApi;
store.fsmDef = props.fsmDef;
store.userId = props.userId;
store.title = props.title;
store.subtitle = props.subtitle;

</script>

<style lang="scss">
@import 'assets/styles/global.scss';
</style>

<style lang="scss" scoped>
@import "../assets/styles/variables";

$widget-open-button-margin: 24px;

.widget-history {
    background: $chatfaq-color-gradient-purple;
    width: 220px;
    height: 580px;
    &.maximized {
        height: 85vh;
    }
    border-radius: 10px 0px 0px 10px;
    border-top: 2px solid $chatfaq-color-primary-500;
    border-bottom: 2px solid $chatfaq-color-primary-500;
    border-left: 2px solid $chatfaq-color-primary-500;
}
.widget-wrapper {
    position: absolute;
    display: flex;
    align-items: stretch;
    flex-flow: row;
    bottom: calc($chatfaq-bubble-button-size + $widget-open-button-margin);
    right: 0px;
    margin: 16px;

    .flex-column {
        &.maximized {
            width: 70vw;
            height: 85vh;
        }
        display: flex;
        width: 400px;
        height: 580px;
        align-items: stretch;
        flex-flow: column;
    }
}


.widget-wrapper > .flex-column > .header {
    border: 2px solid $chatfaq-color-primary-500;
    border-radius: 10px 10px 0px 0px;
    &.history {
        border-radius: 0px 10px 0px 0px;
        border-left: 0px;
    }
}
.widget-wrapper > .flex-column > .chat {
    position: relative;
    height: 100%;
    border-left: 2px solid $chatfaq-color-primary-500;
    border-right: 2px solid $chatfaq-color-primary-500;
    &.history {
        border-left: 0px;
    }
}
.widget-wrapper > .flex-column > .footer {
    border: 2px solid $chatfaq-color-primary-500;
    border-radius: 0px 0px 10px 10px;
    &.history {
        border-radius: 0px 0px 10px 0px;
        border-left: 0px;
    }
}



.widget-open-button {
    cursor: pointer;
    background: $chatfaq-color-gradient-pink;
    &:hover {
        background: $chatfaq-color-gradient-purple;
    }
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

