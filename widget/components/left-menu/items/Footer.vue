<template>
    <div>
        <div class="footer-content">
            <div class="text">
                Powered by
            </div>
            <i alt="ChatFAQ" class="logo-long"/>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";

const store = useGlobalStore();
</script>


<style lang="scss" scoped>

.footer-content {
    display: flex;
    margin-left: 16px;
    > * {

        &.logo-long {
            margin-left: 8px;
            content: $chatfaq-logo-long-icon;
        }

        &.text {
            font: $chatfaq-font-body-xs;
            font-size: 12px;
        }
    }
}

</style>

