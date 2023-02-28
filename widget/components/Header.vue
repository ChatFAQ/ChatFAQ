<template>
    <div class="widget-wrapper-header">
        <i class="logo"/>
        <div class="header-text">
            <div class="title"> {{ store.title }}</div>
            <div class="subtitle"> {{ store.subtitle }}</div>
        </div>
        <i class="menu"/>
        <i class="maximizer"/>
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

    > * {
        margin-top: 30px;
        margin-bottom: 30px;

        &.maximizer {
            cursor: pointer;
            content: $chatfaq-maximize;
            margin-left: 8px;
            margin-right: 24px;

            &.maximized {
                content: $chatfaq-minimize;
            }
        }

        &.menu {
            cursor: pointer;
            margin-left: auto;
            content: $chatfaq-dot-menu;
        }

        &.logo {
            margin-left: 24px;
            margin-right: 16px;
            content: $chatfaq-logo;
        }

        &.header-text {
            .title {
                font: $chatfaq-font-body-m-bold;
            }

            .subtitle {
                font: $chatfaq-font-body-sm;
            }
        }
    }
}

</style>

