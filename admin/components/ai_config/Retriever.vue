<template>
    <ReadView
        :itemName="$t('retriever')"
        :apiUrl="'/api/language-model/retriever-configs/?format=json'"
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
</script>
