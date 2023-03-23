<template>
    <div class="widget-wrapper-header">
        <i class="logo"/>
        <div class="header-text">
            <div class="title"> {{ store.title }}</div>
            <div class="subtitle"> {{ store.subtitle }}</div>
        </div>
        <div class="menu-button" @click="store.menuOpened = !store.menuOpened">
            <i/>
        </div>
        <Menu class="menu" v-if="store.menuOpened"/>
        <div class="maximizer" @click="store.maximized = !store.maximized">
            <i :class="{'maximized': store.maximized}" />
        </div>
    </div>
</template>

<script setup>
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
            margin-left: 10px;
            margin-right: 24px;
            display: flex;
            width: 32px;
            height: 32px;
            border-radius: 32px;

            &:hover {
                background: $chatfaq-color-primary-900;
            }

            i {
                content: $chatfaq-maximize-icon;

                &.maximized {
                    content: $chatfaq-minimize-icon;
                }
            }
        }

        &.menu-button {
            cursor: pointer;
            margin-left: auto;
            position: relative;
            width: 32px;
            height: 32px;
            border-radius: 32px;
            display: flex;

            &:hover {
                background: $chatfaq-color-primary-900;
            }
            i {
                content: $chatfaq-dot-menu-icon;
            }
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

