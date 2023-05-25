<template>
    <div>
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
@import "assets/styles/variables";

.footer-content {
    display: flex;
    justify-content: center;
    > * {

        &.logo-long {
            margin-left: 8px;
            content: $chatfaq-logo-long-icon;
        }

        &.text {
            font: $chatfaq-font-body-xs;
        }
    }
}

</style>

