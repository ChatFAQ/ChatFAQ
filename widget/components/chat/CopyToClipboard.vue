<template>
    <div class="control" :class="{'dark-mode': store.darkMode}">
        <svg v-if="!copied" @click="copy" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
                d="M8.66667 14L2.66667 14C2.29848 14 2 13.7015 2 13.3333L2 4.66667C2 4.29848 2.29848 4 2.66667 4L6.39053 4C6.56734 4 6.73691 4.07024 6.86193 4.19526L9.13807 6.4714C9.2631 6.59643 9.33334 6.766 9.33334 6.94281V13.3333C9.33334 13.7015 9.03486 14 8.66667 14Z"
                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path
                d="M6.66669 4L6.66669 2.66667C6.66669 2.29848 6.96516 2 7.33335 2L11.0572 2C11.234 2 11.4036 2.07024 11.5286 2.19526L13.8048 4.4714C13.9298 4.59643 14 4.766 14 4.94281V11.3333C14 11.7015 13.7015 12 13.3334 12L9.33335 12"
                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 7.33333L6.66667 7.33333C6.29848 7.33333 6 7.03486 6 6.66667L6 4" stroke="currentColor"
                  stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 5.33333L11.3334 5.33333C10.9652 5.33333 10.6667 5.03486 10.6667 4.66667L10.6667 2"
                  stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 8.0003L6.82843 10.8287L12.4853 5.17188" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                  stroke-linejoin="round"/>
        </svg>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import {ref} from "vue";

const props = defineProps(["msgId"]);

const store = useGlobalStore();
const copied = ref(false);

async function copy() {
    const msg = store.getMessageById(props.msgId)
    const text = msg.stack[0].payload.model_response
    navigator.clipboard.writeText(text);
    copied.value = true;
    setTimeout(() => {
        copied.value = false;
    }, 1000)
}

</script>
<style scoped lang="scss">

.control {
    cursor: pointer;
    color: $chatfaq-color-clipboard-text-light;
    padding: 4px;
    margin-top: 6px;
    display: flex;

    &.dark-mode {
        color: $chatfaq-color-clipboard-text-dark;
    }
}

</style>
