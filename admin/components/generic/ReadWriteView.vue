<template>
    <ReadView
        v-if="edit === undefined && !add"
        :apiName="apiName"
        :itemName="itemName"
        :cardProps="cardProps"
        :tableProps="tableProps"
    />
    <WriteView
        v-else
        :apiName="apiName"
        :itemName="itemName"
        :schemaName="schemaName"
        :edit="edit"
        :add="add"
    />
</template>

<script setup>
import ReadView from "~/components/generic/ReadView.vue";
import {defineProps} from 'vue';
import WriteView from "~/components/generic/WriteView.vue";

const props = defineProps({
    apiName: {
        type: String,
        mandatory: true
    },
    itemName: {
        type: String,
        mandatory: true
    },
    schemaName: {
        type: String,
        mandatory: true
    },
    cardProps: {
        type: Object,
        mandatory: true
    },
    tableProps: {
        type: Object,
        mandatory: true
    },
    edit: {
        type: String,
        mandatory: false
    },
    add: {
        type: Boolean,
        mandatory: false
    },
})
</script>
