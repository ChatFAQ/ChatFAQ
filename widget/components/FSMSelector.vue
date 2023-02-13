<template>
    <div class="selector-wrapper">
        <div>Select Your FSM</div>
        <SelectButton v-model="selectedFSMDef" :options="fsmDefs" optionLabel="name"/>
    </div>
</template>

<script setup>
    const runtimeConfig = useRuntimeConfig()
    const { data: fsmDefs } = await useFetch(runtimeConfig.chatfaqAPI + "/back/api/fsm/definitions/?fields=id,name")
    const selectedFSMDef = useState("selectedFSMDef")
</script>

<style scoped lang="scss">
    .selector-wrapper{
        text-align: center;
        * {
            margin: 20px;
        }
    }
</style>
