<template>
    <div class="selector-wrapper">
        <div>Select Your FSM</div>
        <SelectButton v-model="FSMDefStore.selectedFSMDef" :options="fsmDefs" optionLabel="name"/>
    </div>
</template>

<script setup>
    import { useFetch } from "nuxt/app";
    import { useFSMDef } from '~/store/FSMDef'
    const FSMDefStore = useFSMDef();

    const runtimeConfig = useRuntimeConfig()
    const { data: fsmDefs } = await useFetch(runtimeConfig.chatfaqAPI + "/back/api/fsm/definitions/?fields=id,name")

</script>

<style scoped lang="scss">
    .selector-wrapper{
        text-align: center;
        * {
            margin: 20px;
        }
    }
</style>
