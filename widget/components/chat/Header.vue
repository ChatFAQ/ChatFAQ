<template>
    <div class="widget-wrapper-header">
        <div class="menu-button" @click="store.historyOpened = !store.historyOpened">
            <i :class="{'opened': store.historyOpened}"/>
        </div>
        <div class="header-text">
            <div class="title"> {{ store.title }}</div>
            <div class="subtitle"> {{ store.subtitle }}</div>
        </div>
        <div class="maximizer" @click="store.maximized = !store.maximized">
            <i :class="{'maximized': store.maximized}" />
        </div>
        <div class="minimizer" @click="store.opened = false">
            <i/>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";

const store = useGlobalStore();
</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";
$phone-breakpoint: 600px;

.widget-wrapper-header {
    display: flex;
    background: $chatfaq-color-gradient-purple;
    color: $chatfaq-color-neutral-white !important;
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

            &:hover {
                background: $chatfaq-color-primary-900;
            }

            i {
                width: 32px;
                margin: auto;
            }
        }
        &.maximizer {
            i {
                content: $chatfaq-maximize-icon;
                &.maximized {
                    content: $chatfaq-minimize-icon;
                }
            }
            @media only screen and (max-width: $phone-breakpoint) {
                display: none;
            }
        }
        &.minimizer {
            display: none;
            i {
                content: $chatfaq-arrow-down-icon;
            }
            @media only screen and (max-width: $phone-breakpoint) {
                display: unset;
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

            &:hover {
                background: $chatfaq-color-primary-900;
            }
            i {
                width: 20px;
                margin: auto;
                content: $chatfaq-hamburguer-icon;
                &.opened {
                    content: $chatfaq-double-arrow-right-icon;
                }
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

