<template>
    <ReadView
        :itemName="'retriever'"
        :apiUrl="'/api/language-model/retriever-configs/?format=json'"
        :cardProps="{'model_name': 'Model Name', 'batch_size': 'Batch Size', 'device': 'Device'}"
        :tableProps="{'model_name': 'Model Name', 'batch_size': 'Batch Size', 'device': 'Device', 'updated_date': 'Last Modified'}"
    />
</template>

<script setup>

import ReadView from "~/components/generic/ReadView.vue";
</script>
<style lang="scss" scoped>

</style>
