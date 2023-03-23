<template>
    <div class="conversations">
        <div class="conversation-item new-conversation">
            <HistoryNewConversationItem></HistoryNewConversationItem>
        </div>
        <div v-for="conversation in conversations" class="conversation-item">
            <HistoryItem :conversation-id="conversation[0]" :title="conversation[1]"/>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useGlobalStore } from "~/store";

const store = useGlobalStore();

const conversations = ref()

let response = await fetch(store.chatfaqAPI + `/back/api/broker/conversations_info?transmitter_id=${store.userId}`);
conversations.value = await response.json();

function timestampToSentence(isoString) {
    return (new Date(isoString)).toString().split(" GMT")[0]
}

</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.conversations {
    font-size: 14px;
    overflow-y: scroll;
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
    &::-webkit-scrollbar {
        display: none;
    }

    .conversation-item {
        &.new-conversation {
            margin-top: 16px;
            background: rgba(223, 218, 234, 0.1);
        }
        margin-left: 14px;
        margin-right: 14px;

        padding: 7px 10px;

        &:hover {
            // background: rgba(223, 218, 234, 0.1);
            cursor: pointer;
        }

    }
}
</style>

