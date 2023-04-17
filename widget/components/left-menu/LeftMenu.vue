<template>
    <div class="left-menu-wrapper">
        <div class="close-menu" @click="store.historyOpened = false">
            <i/>
        </div>
        <div class="new-conversation">
            <div class="left-menu-item">
                <NewConversationItem/>
            </div>

        </div>
        <div class="conversations">
            <div v-for="conversation in store.conversations" class="left-menu-item">
                <HistoryItem :key="conversation[0]" :conversation-id="conversation[0]" :title="conversation[1]"/>
            </div>
        </div>
        <div class="other-buttons">

            <div class="left-menu-item">
                <DownloadHistory/>
            </div>

            <div class="left-menu-item">
                <LightMode/>
            </div>

            <div class="left-menu-item">
                <DeleteHistory/>
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

const store = useGlobalStore();

await store.gatherConversations()

</script>


<style lang="scss" scoped>
@import "assets/styles/variables";
$phone-breakpoint: 600px;

.left-menu-wrapper {
    display: flex;
    flex-direction: column;
    font-size: 14px;
    color: $chatfaq-color-neutral-white;

    @media only screen and (max-width: $phone-breakpoint) {
        position: absolute;
        z-index: 2;
        height: 100% !important;
    }
    .conversations {
        height: 100%;
        overflow-y: scroll;
        -ms-overflow-style: none; /* IE and Edge */
        scrollbar-width: none; /* Firefox */
        &::-webkit-scrollbar {
            display: none;
        }

        &:first-child {
            margin-top: 16px;
        }
    }


    .new-conversation {
        .left-menu-item {
            margin-top: 16px;
            margin-bottom: 8px;
            background: rgba(223, 218, 234, 0.1);
        }
    }

    .left-menu-item {
        margin-left: 14px;
        margin-right: 14px;


        &:hover {
            cursor: pointer;
        }

    }

    .other-buttons {
        height: fit-content;
        display: flex;
        flex-direction: column-reverse;
        > div:last-child {
            border-top: 2px solid #4D4160;
        }


        .left-menu-item {
            margin-left: 0px;
            margin-right: 0px;
            padding-left: 14px;
            padding-right: 14px;

            &:first-child {
                margin-bottom: 16px;
            }

            &:hover {
                background-color: $chatfaq-color-primary-900;
            }
        }
    }
    .close-menu {
        position: absolute;
        right: -50px;
        background-color: $chatfaq-color-primary-500;
        border-radius: 20px;
        width: 32px;
        top: 30px;
        height: 32px;
        align-content: center;
        align-items: center;
        justify-content: center;
        i {
            content: $chatfaq-double-arrow-left-icon;
            width: 16px;
        }
        @media only screen and (max-width: $phone-breakpoint) {
            display: flex;
        }
    }
}
</style>

