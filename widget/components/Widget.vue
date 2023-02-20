<template>
    <FSMSelector v-if="!selectedFSMDef"></FSMSelector>
    <Chat v-else/>
</template>

<script setup>
import FSMSelector from "~/components/FSMSelector.vue";
import Chat from "~/components/Chat.vue";
import { useState } from "nuxt/app";

const selectedFSMDef = useState("selectedFSMDef")
</script>

<style scoped>

</style>
