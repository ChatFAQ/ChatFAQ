<template>
    <ReadView
        :itemType="$t('retriever-configs')"
        :itemName="$t('retriever')"
        :apiUrl="'/api/language-model/retriever-configs/'"
        :cardProps="{
            'model_name': $t('modelname'),
            'batch_size': $t('batchsize'),
            'device': $t('device'),
        }"
        :tableProps="{
            'model_name': $t('modelname'),
            'batch_size': $t('batchsize'),
            'device': $t('device'),
            'updated_date': $t('updateddate'),
        }"
    />
</template>

<script setup>
import ReadView from "~/components/generic/ReadView.vue";
import {defineProps} from 'vue';

const props = defineProps({
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
