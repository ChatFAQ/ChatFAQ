<template>
    <div>
        <div class="footer-content">
            <div class="text">
                Powered by
            </div>
            <LogoLong alt="ChatFAQ" class="logo-long"/>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import LogoLong from "~/components/icons/LogoLong.vue";

const store = useGlobalStore();
</script>


<style lang="scss" scoped>

.footer-content {
    display: flex;
    margin-left: 16px;
    > * {

        &.logo-long {
            margin-left: 8px;
            margin-top: auto;
            margin-bottom: auto;
        }

        &.text {
            font: $chatfaq-font-body-xs;
            font-size: 12px;
        }
    }
}

</style>

