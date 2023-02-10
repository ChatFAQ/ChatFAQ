<template>
    <div class="selector-wrapper">
        <div>Select Your FSM</div>
        <SelectButton v-model="selectedFSMDef" :options="fsmDefs" optionLabel="name" />
    </div>
</template>

<script setup>
const fsmDefs = ref(null);
const runtimeConfig = useRuntimeConfig();
const selectedFSMDef = useState("selectedFSMDef");

const res = await fetch(runtimeConfig.riddlerAPI + "/back/api/fsm/definitions/?fields=id,name");
fsmDefs.value = await res.json();
</script>

<style scoped lang="scss">
.selector-wrapper {
    text-align: center;

    * {
        margin: 20px;
    }
}
</style>
