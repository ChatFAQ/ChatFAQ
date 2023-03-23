<template>
    <div class="left-menu-wrapper">
        <div class="conversations">
            <div class="left-menu-item new-conversation">
                <HistoryNewConversationItem/>
            </div>
            <div v-for="conversation in conversations" class="left-menu-item">
                <HistoryItem :conversation-id="conversation[0]" :title="conversation[1]"/>
            </div>
        </div>
        <div class="other-buttons">
            <div class="left-menu-item" @click="store.darkMode = !store.darkMode">
                <MenuItem>
                        <i class="light-mode-icon" :class="{'dark-mode': store.darkMode}"/>
                        <span v-if="!store.darkMode">Show dark mode</span>
                        <span v-else>{{ $t("showlightmode") }}</span>
                </MenuItem>
            </div>

            <div class="left-menu-item" @click="store.darkMode = !store.darkMode">
                <MenuItem>
                    <i class="email-icon"/>
                    <span>{{ $t("sendasummary") }}</span>
                </MenuItem>
            </div>

        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useGlobalStore } from "~/store";
import HistoryNewConversationItem from "~/components/left-menu/HistoryNewConversationItem.vue";
import HistoryItem from "~/components/left-menu/HistoryItem.vue";
import MenuItem from "~/components/left-menu/MenuItem.vue";

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

.left-menu-wrapper {
    display: flex;
    flex-direction: column;
    font-size: 14px;
    color: $chatfaq-color-neutral-white;

    .conversations {
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
    .other-buttons {
        height: 100%;
        display: flex;
        flex-direction: column-reverse;
        .left-menu-item {
            &:first-child {
                margin-bottom: 16px;
            }

            .light-mode-icon {
                content: $chatfaq-moon-icon;

                &.dark-mode {
                    content: $chatfaq-sun-icon;
                }
            }

            .email-icon {
                content: $chatfaq-mail-icon;
            }
        }
    }

    .left-menu-item {
        &.new-conversation {
            background: rgba(223, 218, 234, 0.1);
        }
        margin-left: 14px;
        margin-right: 14px;

        &:hover {
            // background: rgba(223, 218, 234, 0.1);
            cursor: pointer;
        }

    }
}
</style>

