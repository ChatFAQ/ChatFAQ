<template>
    <div class="left-menu-wrapper">
        <div class="new-conversation">
            <div class="left-menu-item">
                <NewConversationItem/>
            </div>

        </div>
        <div class="conversations">
            <div v-for="conversation in conversations" class="left-menu-item">
                <HistoryItem :conversation-id="conversation[0]" :title="conversation[1]"/>
            </div>
        </div>
        <div class="other-buttons">

            <div class="left-menu-item">
                <SendEmail/>
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
import {ref} from 'vue';
import {useGlobalStore} from "~/store";
import NewConversationItem from "~/components/left-menu/items/NewConversationItem.vue";
import HistoryItem from "~/components/left-menu/items/HistoryItem.vue";
import LightMode from "~/components/left-menu/items/LightMode.vue";
import SendEmail from "~/components/left-menu/items/SendEmail.vue";
import DeleteHistory from "~/components/left-menu/items/DeleteHistory.vue";

const store = useGlobalStore();

const conversations = ref()

let response = await fetch(store.chatfaqAPI + `/back/api/broker/conversations?id=${store.userId}`);
conversations.value = await response.json();

</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.left-menu-wrapper {
    display: flex;
    flex-direction: column;
    font-size: 14px;
    color: $chatfaq-color-neutral-white;

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
            // background: rgba(223, 218, 234, 0.1);
            cursor: pointer;
        }

    }
    .other-buttons {
        height: fit-content;
        display: flex;
        flex-direction: column-reverse;

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
}
</style>

