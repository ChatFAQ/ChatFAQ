<template>
    <div class="left-menu-wrapper">
        <div class="menu-button" @click="store.historyOpened = !store.historyOpened">
            <DoubleArrowLeft v-if="store.historyOpened" class="double-arrow-left"/>
            <BurgerMenu v-else class="burger-menu"/>
        </div>
        <div class="new-conversation">
            <div class="left-menu-item">
                <NewConversationItem/>
            </div>

        </div>
        <div class="conversations">
            <div v-for="conversation in store.conversations" class="left-menu-item">
                <HistoryItem
                    ref="historyItems"
                    :key="conversation.id"
                    :conversation-id="conversation.id"
                    :platform-conversation-id="conversation.platform_conversation_id"
                    :name="conversation.name"/>
            </div>
        </div>
        <div class="other-buttons">
            <Footer class="footer" :class="{'history': store.historyOpened}"/>

            <div class="left-menu-item" v-if="store.enableLogout">
                <LogOut/>
            </div>

            <div class="left-menu-item">
                <DeleteHistory/>
            </div>

            <div class="left-menu-item">
                <DownloadHistory/>
            </div>

            <div class="left-menu-item" v-if="!store.disableDayNightMode && (!store.selectedConversations || !store.selectedConversations.length)">
                <LightMode/>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import NewConversationItem from "~/components/left-menu/items/NewConversationItem.vue";
import HistoryItem from "~/components/left-menu/items/HistoryItem.vue";
import LightMode from "~/components/left-menu/items/LightMode.vue";
import DownloadHistory from "~/components/left-menu/items/DownloadHistory.vue";
import DeleteHistory from "~/components/left-menu/items/DeleteHistory.vue";
import Footer from "~/components/left-menu/items/Footer.vue";
import BurgerMenu from "~/components/icons/BurgerMenu.vue";
import DoubleArrowLeft from "~/components/icons/DoubleArrowLeft.vue";
import {ref, watch} from "vue";
import LogOut from "~/components/left-menu/items/LogOut.vue";

const historyItems = ref(null)

const store = useGlobalStore();

watch(() => store.deleting, (newVal) => {
    if (newVal && !store.selectedConversations.length) {
        historyItems.value.forEach(el => el.selected = true)
    } else if (!newVal && !store.downloading && store.selectedConversations.length === store.conversationsIds.length) {
        historyItems.value.forEach(el => el.selected = false)
    }
})
watch(() => store.downloading, (newVal) => {
    if (newVal && !store.selectedConversations.length) {
        historyItems.value.forEach(el => el.selected = true)
    } else if (!newVal && !store.deleting && store.selectedConversations.length === store.conversationsIds.length) {
        historyItems.value.forEach(el => el.selected = false)
    }
})

</script>


<style lang="scss" scoped>

$phone-breakpoint: 600px;
$history-width: 220px;

.left-menu-wrapper {
    display: flex;
    flex-direction: column;
    font-size: 14px;
    color: $chatfaq-color-menu-text;

    @media only screen and (max-width: $phone-breakpoint) {
        position: absolute;
        z-index: 2;
        height: 100% !important;
        border-radius: unset !important;
    }

    .conversations {
        height: 100%;
        overflow-x: hidden;

        &:first-child {
            margin-top: 16px;
        }

        @include scroll-style($chatfaq-color-menu-scrollColor);
    }


    .new-conversation {
        .left-menu-item {
            margin-top: 16px;
            margin-bottom: 8px;
            background: $chatfaq-color-menuItem-background;
            border-radius: 4px;
        }

        .menu-item {
            display: flex;
            padding: 10px 8px !important;
        }
    }

    .left-menu-item {
        margin-left: 8px;
        margin-right: 8px;


        &:hover {
            cursor: pointer;
        }

    }

    .other-buttons {
        height: fit-content;
        display: flex;
        flex-direction: column-reverse;

        > .left-menu-item:last-child {
            border-top: 1px solid $chatfaq-color-menu-border;
            padding-top: 12px;
        }

        > .left-menu-item:nth-child(2) {
            padding-bottom: 12px;
        }

        > .footer {
            border-top: 1px solid $chatfaq-color-menu-border;
            padding-top: 20px;
            padding-bottom: 20px;
            height: 60px;
        }


        .left-menu-item {
            margin-left: 8px;
            margin-right: 8px;
            padding-left: 0px;
            padding-right: 0px;

            .menu-item {
                padding: 12px 8px;
                margin: 4px 0px;
            }

            &:first-child {
                margin-bottom: 16px;
            }
        }
    }

    .menu-button {
        display: none;
        @media only screen and (max-width: $phone-breakpoint) {
            position: absolute;
            left: $history-width;
            margin-left: 60px;
            margin-top: 30px;
            cursor: pointer;
            border-radius: 32px;
            height: 40px;
            width: 40px;
            display: flex;
            border: 1px solid $chatfaq-color-menu-border;
            background: $chatfaq-color-menuButton-background;
            .burger-menu {
                width: 20px;
                margin: auto;
                color: $chatfaq-burger-menu-icon-color;
            }
            .double-arrow-left {
                width: 20px;
                margin: auto;
                color: $chatfaq-double-arrow-left-icon-color;
            }
        }
    }
}
</style>

