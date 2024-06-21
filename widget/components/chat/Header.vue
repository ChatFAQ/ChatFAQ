<template>
    <div class="widget-wrapper-header">
        <div class="menu-button" @click="store.historyOpened = !store.historyOpened">
            <DoubleArrowRight v-if="store.historyOpened" class="double-arrow-right"/>
            <BurgerMenu v-else class="burger-menu"/>
        </div>
        <div class="header-text">
            <div class="title"> {{ store.title }}</div>
            <div class="subtitle"> {{ store.subtitle }}</div>
        </div>
        <div class="maximizer" v-if="!store.fullScreen" @click="store.maximized = !store.maximized; store.scrollToBottom += 1">
            <Minimize class="max-icon" v-if="store.maximized"/>
            <Maximize class="min-icon" v-else/>
        </div>
        <div class="minimizer" v-if="!store.fullScreen" @click="store.opened = false">
            <ArrowDown class="min-icon"/>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import Maximize from "~/components/icons/Maximize.vue";
import Minimize from "~/components/icons/Minimize.vue";
import ArrowDown from "~/components/icons/ArrowDown.vue";
import BurgerMenu from "~/components/icons/BurgerMenu.vue";
import DoubleArrowRight from "~/components/icons/DoubleArrowRight.vue";

const store = useGlobalStore();
</script>


<style lang="scss" scoped>

$phone-breakpoint: 600px;

.widget-wrapper-header {
    display: flex;
    background: $chatfaq-color-menu-background;
    color: $chatfaq-color-menu-text !important;
    /*
    .menu {
        margin: 0px;
        position: absolute;
        z-index: 1;
        top: 80px;
        right: 60px;;
    }
    */

    > * {
        margin-top: 30px;
        margin-bottom: 30px;

        &.maximizer, &.minimizer {
            cursor: pointer;
            margin-left: auto;
            margin-right: 24px;
            display: flex;
            width: 40px;
            border-radius: 32px;
            border: 1px solid $chatfaq-color-menu-border;

            &:hover {
                background: $chatfaq-color-menuItem-background-hover;
            }

            i {
                width: 24px;
                margin: auto;
            }
        }
        &.maximizer {
            border: 1px solid $chatfaq-color-menu-border;
            .max-icon {
                margin: auto;
                color: $chatfaq-maximize-icon-color;
            }
            .min-icon {
                margin: auto;
                color: $chatfaq-minimize-icon-color;
            }
            @media only screen and (max-width: $phone-breakpoint) {
                display: none;
            }
        }
        &.minimizer {
            display: none;
            @media only screen and (max-width: $phone-breakpoint) {
                display: flex;
            }
            .min-icon {
                margin: auto;
                color: $chatfaq-arrow-down-icon-color;
            }
        }

        &.menu-button {
            cursor: pointer;
            margin-left: 24px;
            margin-right: 16px;
            position: relative;
            border-radius: 32px;
            width: 40px;
            display: flex;
            border: 1px solid $chatfaq-color-menu-border;

            &:hover {
                background: $chatfaq-color-menuItem-background-hover;
            }
            .burger-menu {
                width: 20px;
                margin: auto;
                color: $chatfaq-burger-menu-icon-color;
            }
            .double-arrow-right {
                width: 20px;
                margin: auto;
                color: $chatfaq-double-arrow-right-icon-color;
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

