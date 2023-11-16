<template>
    <ReadView
        v-if="edit === undefined && !add"
        :apiName="'retriever-configs'"
        :itemName="'retriever'"
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
    <WriteView
        v-else
        :apiName="'retriever-configs'"
        :itemName="'retriever'"
        :schemaName="'RetrieverConfig'"
        :edit="edit"
        :add="add"
    />
</template>

<script setup>
import ReadView from "~/components/generic/ReadView.vue";
import {defineProps} from 'vue';
import WriteView from "~/components/generic/WriteView.vue";

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
