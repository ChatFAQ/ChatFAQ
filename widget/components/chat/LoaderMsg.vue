<template>
    <div class="message-wrapper bot is-last" :class="{ 'maximized': store.maximized }">

        <div class="message bot is-last" :class="{ 'maximized': store.maximized }">
            <div class="content bot is-last-of-type"
                 :class="{
                'dark-mode': store.darkMode,
                'maximized': store.maximized,
            }">
                <!--<Loader v-if="store.darkMode"/>
                <Loader v-else color="#463075"/>-->
                <Loader :color="store.darkMode" />
            </div>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import Loader from "~/components/generic/Loader.vue";

const store = useGlobalStore();

</script>
<style scoped lang="scss">
@import "assets/styles/variables";

$phone-breakpoint: 600px;

.message-wrapper {
    display: flex;
    flex-direction: column;
    margin-left: 24px;
    margin-right: 86px;

    &.maximized {
        @media only screen and (min-width: $phone-breakpoint) {
            margin-right: 35vw;
        }
    }
}


.content {
    padding: 15px;
    word-wrap: break-word;
    max-width: 100%;

    background-color: $chatfaq-color-chatMessageBot-background-light;
    color: $chatfaq-color-chatMessageBot-text-light;
    border-radius: 6px 6px 6px 0px;

    &.dark-mode {
        background-color: $chatfaq-color-chatMessageBot-background-dark;
        color: $chatfaq-color-chatMessageBot-text-dark;
    }
}

.message {
    display: flex;
    align-items: baseline;
    flex-direction: column;
    max-width: 100%;
    height: 100%;
    margin: 8px 0px 20px;

}
</style>
