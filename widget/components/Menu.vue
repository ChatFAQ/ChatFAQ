<template>
    <div class="menu-wrapper">
        <div class="menu-button" @click="store.darkMode = !store.darkMode">
            <i class="light-mode-icon" :class="{'dark-mode': store.darkMode}"/>
            <span v-if="!store.darkMode">Show dark mode</span>
            <span v-else>{{ $t("showlightmode") }}</span>
        </div>
        <div class="menu-button" @click="store.historyOpened = !store.historyOpened"><i class="history-icon"/>{{ $t("showhistory") }}</div>
        <div class="menu-button"><i class="email-icon"/>{{ $t("sendasummarybyemail") }}</div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";

const store = useGlobalStore();


</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.menu-wrapper {
    display: flex;
    flex-direction: column;
    background-color: white;
    color: $chatfaq-color-neutral-black;
    border-radius: 10px;
    font: $chatfaq-font-body-s;
    line-height: 24px;
    overflow: hidden;

    > * {
        padding: 10px 18px 10px 18px;
    }

    i {
        margin-right: 10px;
    }

    .light-mode-icon {
        content: $chatfaq-moon-icon;

        &.dark-mode {
            content: $chatfaq-sun-icon;
        }
    }

    .history-icon {
        content: $chatfaq-clock;
    }

    .email-icon {
        content: $chatfaq-mail-icon;
    }

    .menu-button {
        cursor: pointer;

        &:hover {
            background-color: $chatfaq-color-primary-200;
        }
    }
}
</style>

