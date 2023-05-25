<template>
    <div class="left-menu-wrapper">
        <div class="new-conversation">
            <div class="left-menu-item">
                <NewConversationItem/>
            </div>

        </div>
        <div class="conversations">
            <div v-for="conversation in store.conversations" class="left-menu-item">
                <HistoryItem ref="historyItems" :key="conversation[0]" :conversation-id="conversation[0]"
                             :title="conversation[1]"/>
            </div>
        </div>
        <div class="other-buttons">
            <Footer class="footer" :class="{'history': store.historyOpened}"/>

            <div class="left-menu-item delete-history">
                <DeleteHistory/>
            </div>

            <div class="left-menu-item">
                <DownloadHistory/>
            </div>

            <div class="left-menu-item">
                <LightMode/>
            </div>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import NewConversationItem from "~/components/left-menu/items/NewConversationItem.vue";
import HistoryItem from "~/components/left-menu/items/HistoryItem.vue";
import LightMode from "~/components/left-menu/items/LightMode.vue";
import DownloadHistory from "~/components/left-menu/items/DownloadHistory.vue";
import DeleteHistory from "~/components/left-menu/items/DeleteHistory.vue";
import Footer from "~/components/left-menu/items/Footer.vue";

const historyItems = ref(null)

const store = useGlobalStore();

await store.gatherConversations()


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
            border-radius: 4px;
        }
        .menu-item {
            display: flex;
            padding: 10px 4px !important;
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
            border-top: 1px solid $chatfaq-color-neutral-purple;
            padding-top: 12px;
        }

        > .delete-history {
            padding-bottom: 12px;
        }

        > .footer {
            border-top: 1px solid $chatfaq-color-neutral-purple;
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
}
</style>

