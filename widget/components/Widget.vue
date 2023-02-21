<template>
    <FSMSelector v-if="!FSMDefStore.selectedFSMDef.id"></FSMSelector>
    <Chat v-else/>
</template>

<script setup>
import FSMSelector from "~/components/FSMSelector.vue";
import Chat from "~/components/Chat.vue";
import { useFSMDef } from '~/store/FSMDef'
const FSMDefStore = useFSMDef();

</script>

<style scoped>

</style>
