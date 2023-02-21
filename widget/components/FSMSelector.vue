<template>
    <div class="selector-wrapper">
        <div>Select Your FSM</div>
        <SelectButton v-model="FSMDefStore.selectedFSMDef" :options="fsmDefs" optionLabel="name"/>
    </div>
</template>

<script setup>
import {useFSMDef} from '~/store/FSMDef'
import { ref } from 'vue';

const FSMDefStore = useFSMDef();

const fsmDefs = ref()

const runtimeConfig = useRuntimeConfig()

let response = await fetch(runtimeConfig.chatfaqAPI + "/back/api/fsm/definitions/?fields=id,name");
fsmDefs.value = await response.json();

</script>

<style scoped lang="scss">
.selector-wrapper {
    text-align: center;

    * {
        margin: 20px;
    }
}
</style>
