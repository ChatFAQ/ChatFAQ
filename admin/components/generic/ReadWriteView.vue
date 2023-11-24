<template>
    <ReadView
        v-if="editing === undefined && !adding"
        :apiUrl="apiUrl"
        :readableName="readableName"
        :cardProps="cardProps"
        :tableProps="tableProps"
        :titleProp="titleProp"
    />
    <WriteView
        v-else
        :readableName="readableName"
        :apiUrl="apiUrl"
        :editing="editing"
        :adding="adding"
        :titleProp="titleProp"
        v-bind="$attrs"
    >
        <template v-for="(_, name) in $slots" v-slot:[name]="data">
            <slot :name="name" v-bind="data"></slot>
        </template>
    </WriteView>
</template>

<script setup>
import ReadView from "~/components/generic/ReadView.vue";
import {defineProps} from 'vue';
import WriteView from "~/components/generic/WriteView.vue";
import {storeToRefs} from 'pinia'
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()


const {editing, adding} = storeToRefs(itemsStore)

const props = defineProps({
    readableName: {
        type: String,
        mandatory: true
    },
    apiUrl: {
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
    titleProp: {
        type: String,
        required: false,
        default: "name",
    },
})
</script>
