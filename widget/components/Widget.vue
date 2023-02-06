<template>
    <FSMSelector v-if="!selectedFSMDef"></FSMSelector>
    <Chat v-else/>
</template>

<script setup>
const selectedFSMDef = useState("selectedFSMDef")
</script>

<style scoped>

</style>