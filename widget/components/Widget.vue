<template>
    <Suspense>
        <div class="chatfaq-widget">
            <div v-if="store.opened" class="widget-wrapper" :class="{'history': store.historyOpened}">
                <div class="dark-filter" v-if="store.historyOpened"></div>
                <LeftMenu v-if="store.historyOpened" class="widget-history" :class="{'maximized': store.maximized}"/>
                <div class="widget-body" :class="{'maximized': store.maximized, 'history-closed': !store.historyOpened}">
                    <Header class="header" :class="{'history': store.historyOpened}"/>
                    <Chat class="chat" :class="{'history': store.historyOpened}"/>
                </div>
            </div>
            <div class="widget-open-button" :class="{'opened': store.opened}"
                 @click="store.opened = !store.opened">
                <i :class="store.opened ? 'close' : 'open'"/>
            </div>
        </div>
    </Suspense>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import { ref, defineProps } from "vue";
import LeftMenu from "~/components/left-menu/LeftMenu.vue";
import Header from "~/components/chat/Header.vue";
import Chat from "~/components/chat/Chat.vue";

const store = useGlobalStore();

const props = defineProps([
    "chatfaqWs",
    "chatfaqApi",
    "fsmDef",
    "userId",
    "title",
    "subtitle",
    "maximized",
    "historyOpened"
]);

store.chatfaqWS = props.chatfaqWs;
store.chatfaqAPI = props.chatfaqApi;
store.fsmDef = props.fsmDef;
store.userId = props.userId;
store.title = props.title;
store.subtitle = props.subtitle;

if (props.maximized !== undefined)
    store.maximized = props.maximized;
if (props.historyOpened !== undefined)
    store.historyOpened = props.historyOpened;

</script>

<style lang="scss">
@import 'assets/styles/global.scss';
</style>

<style lang="scss" scoped>
@import "assets/styles/variables";

$widget-open-button-margin: 24px;
$history-width: 230px;
$history-width-mobile: 260px;
$phone-breakpoint: 600px;
$widget-margin: 16px;

.dark-filter {
    display: none;

    position: absolute;
    width: 100vw;
    height: 100vh;
    background-color: rgba(2, 12, 28, 0.7);
    z-index: 1;
    @media only screen and (max-width: $phone-breakpoint) {
        display: unset;
    }
}

.widget-history {
    background: $chatfaq-color-gradient-purple;
    width: $history-width;
    height: 580px;

    @media only screen and (max-width: $phone-breakpoint) {
        width: $history-width-mobile;
        border-right: 1px solid $chatfaq-color-neutral-purple;
    }
    &.maximized {
        height: 85vh;
    }

    border-radius: 10px 0px 0px 10px;
    border-top: 1px solid $chatfaq-color-neutral-purple;
    border-left: 1px solid $chatfaq-color-neutral-purple;
    border-bottom: 1px solid $chatfaq-color-neutral-purple;
}

.widget-wrapper {
    position: absolute;
    display: flex;
    align-items: stretch;
    flex-flow: row;
    bottom: calc($chatfaq-bubble-button-size + $widget-open-button-margin);
    right: 0px;
    margin: $widget-margin;

    .widget-body {
        &.maximized {
            @media only screen and (min-width: $phone-breakpoint) {
                width: calc(100vw - $history-width - $widget-margin * 2);
                height: 85vh;
            }
            &.history-closed {
                @media only screen and (min-width: $phone-breakpoint) {
                    width: calc(100vw - $widget-margin * 2);
                }
            }
        }

        display: flex;
        width: 400px;
        height: 580px;
        align-items: stretch;
        flex-flow: column;
        @media only screen and (max-width: $phone-breakpoint) {
            width: 100%;
            height: 100%;
        }
    }

    @media only screen and (max-width: $phone-breakpoint) {
        width: 100%;
        height: 100%;
        margin: 0px;
        bottom: 0px;
    }
}


.widget-wrapper > .widget-body > .header {
    border: 1px solid $chatfaq-color-neutral-purple;
    border-radius: 10px 10px 0px 0px;

    &.history {
        border-radius: 0px 10px 0px 0px;
        border-left: 0px;
    }

    @media only screen and (max-width: $phone-breakpoint) {
        border-radius: unset;
    }
}

.widget-wrapper > .widget-body > .chat {
    position: relative;
    height: 100%;
    border-left: 1px solid $chatfaq-color-neutral-purple;
    border-right: 1px solid $chatfaq-color-neutral-purple;
    border-bottom: 1px solid $chatfaq-color-neutral-purple;
    border-radius: 0px 0px 10px 10px;

    &.history {
        border-radius: 0px 0px 10px 0px;
    }

    @media only screen and (max-width: $phone-breakpoint) {
        border-radius: unset;
    }
}

/*
.widget-wrapper > .widget-body > .footer {
    border: 1px solid $chatfaq-color-neutral-purple;
    border-radius: 0px 0px 10px 10px;

    &.history {
        border-radius: 0px 0px 10px 0px;
        border-left: 0px;
    }

    @media only screen and (max-width: $phone-breakpoint) {
        border-radius: unset;
    }
}

*/

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

    &.opened {
        @media only screen and (max-width: $phone-breakpoint) {
            display: none;
        }
    }

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

