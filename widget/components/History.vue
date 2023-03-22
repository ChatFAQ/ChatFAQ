<template>
    <div class="conversations">
        <div v-for="conversation in conversations" class="conversation">
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
    overflow-y: scroll;
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
    &::-webkit-scrollbar {
        display: none;
    }

    .conversation {
        margin-left: 14px;
        margin-right: 14px;

        padding-left: 10px;
        padding-right: 10px;
        padding-top: 7px;
        padding-bottom: 7px;

        &:hover {
            background: rgba(223, 218, 234, 0.1);
            cursor: pointer;
        }

    }
}
</style>

