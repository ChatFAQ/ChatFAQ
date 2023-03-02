<template>
    <div class="widget-wrapper-header">
        <i class="logo"/>
        <div class="header-text">
            <div class="title"> {{ store.title }}</div>
            <div class="subtitle"> {{ store.subtitle }}</div>
        </div>
        <i class="menu-button" @click="store.menuOpened = !store.menuOpened"/>
        <Menu class="menu" v-if="store.menuOpened"/>
        <i class="maximizer" :class="{'maximized': store.maximized}" @click="store.maximized = !store.maximized"/>
    </div>
</template>

<script setup>
import Menu from "~/components/Menu.vue";

import {useGlobalStore} from "~/store";

const store = useGlobalStore();
</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.widget-wrapper-header {
    display: flex;
    background: $chatfaq-color-gradient-purple;
    color: $chatfaq-color-neutral-white !important;

    .menu {
        margin: 0px;
        position: absolute;
        z-index: 1;
        top: 80px;
        right: 60px;;
    }

    > * {
        margin-top: 30px;
        margin-bottom: 30px;

        &.maximizer {
            cursor: pointer;
            content: $chatfaq-maximize-icon;
            margin-left: 8px;
            margin-right: 24px;

            &.maximized {
                content: $chatfaq-minimize-icon;
            }
        }

        &.menu-button {
            cursor: pointer;
            margin-left: auto;
            content: $chatfaq-dot-menu-icon;
            position: relative;
        }

        &.logo {
            margin-left: 24px;
            margin-right: 16px;
            content: $chatfaq-logo-icon;
        }

        &.header-text {
            .title {
                font: $chatfaq-font-body-m-bold;
            }

            .subtitle {
                font: $chatfaq-font-body-s;
            }
        }
    }
}

</style>

