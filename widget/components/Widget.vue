<template>
    <FSMSelector v-if="!store.selectedFSMDef.id"></FSMSelector>
    <Chat v-else/>
</template>

<script setup>
import FSMSelector from "~/components/FSMSelector.vue";
import Chat from "~/components/Chat.vue";
import { useGlobalStore } from '~/store'
const store = useGlobalStore();

</script>

<style scoped>

</style>
