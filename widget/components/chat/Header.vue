<template>
    <div class="widget-wrapper-header">
        <div class="menu-button" @click="store.historyOpened = !store.historyOpened">
            <i :class="{'opened': store.historyOpened}"/>
        </div>
        <div class="header-text">
            <div class="title"> {{ store.title }}</div>
            <div class="subtitle"> {{ store.subtitle }}</div>
        </div>
        <div class="maximizer" v-if="!store.fullScreen" @click="store.maximized = !store.maximized; store.scrollToBottom += 1">
            <i :class="{'maximized': store.maximized}" />
        </div>
        <div class="minimizer" v-if="!store.fullScreen" @click="store.opened = false">
            <i/>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";

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
            i {
                content: $chatfaq-maximize-icon;
                &.maximized {
                    width: 20px;
                    @media only screen and (min-width: $phone-breakpoint) {
                        content: $chatfaq-minimize-icon;
                        width: 24px;
                    }
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
                display: flex;
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
                i {
                    width: 20px;
                    margin: auto;
                }
            }
            i {
                width: 20px;
                margin: auto;
                content: $chatfaq-burger-menu-icon;
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

