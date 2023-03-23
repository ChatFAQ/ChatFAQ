<template>
    <div class="widget-wrapper-header">
        <div class="footer-content">
            <div class="text">
                Powered By
            </div>
            <i class="logo-long"/>
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
    background: $chatfaq-color-gradient-purple;
    color: $chatfaq-color-neutral-white !important;
    .footer-content {
        display: flex;
        justify-content: center;
        > * {
            margin-top: 2px;
            margin-bottom: 6px;

            &.logo-long {
                margin-left: 8px;
                content: $chatfaq-logo-long-icon;
            }

            &.text {
                font: $chatfaq-font-body-xs;
            }
        }
    }
}

</style>

