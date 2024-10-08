<template>
    <div class="control" :class="{'dark-mode': store.darkMode}">
        <Copy v-if="!copied" @click="copy" />
        <Check v-else/>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import {ref} from "vue";
import Copy from "~/components/icons/Copy.vue";
import Check from "~/components/icons/Check.vue";

const props = defineProps(["msgId"]);

const store = useGlobalStore();
const copied = ref(false);

async function copy() {
    const msg = store.getMessageById(props.msgId)
    const text = msg.stack[0].payload.content
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
    color: $chatfaq-color-thumbs-and-clipboard-light;
    margin-top: 6px;
    display: flex;

    &.dark-mode {
        color: $chatfaq-color-thumbs-and-clipboard-dark;
    }
}

</style>
