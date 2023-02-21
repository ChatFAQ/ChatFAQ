<template>
    <div class="selector-wrapper">
        <div>Select Your FSM</div>
        <SelectButton v-model="store.selectedFSMDef" :options="fsmDefs" optionLabel="name"/>
    </div>
</template>

<script setup>
import {useGlobalStore} from '~/store'
import { ref } from 'vue';

const store = useGlobalStore();

const fsmDefs = ref()

let response = await fetch(store.chatfaqAPI + "/back/api/fsm/definitions/?fields=id,name");
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
