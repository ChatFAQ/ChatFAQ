<template>
    <el-collapse>
        <el-collapse-item v-for="(dataSource, index) in dataSources" :title="$t('datasource', {index})" :name="index">
            <WriteView
                :readableName="'Data Sources'"
                :apiUrl="endpoint"
                :itemId="dataSource.id"
            >
            </WriteView>
      </el-collapse-item>
        1<div v-if="!addingDataSource" @click="addDataSource">{{ $t('adddatasource') }}</div>2
    </el-collapse>
</template>


<script setup>
import WriteView from "~/components/generic/WriteView.vue";
import { useItemsStore } from "~/store/items.js";
const endpoint = ref("/back/api/language-model/data-sources/")
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const dataSources = ref([])
dataSources.value = await itemsStore.requestOrGetItems($axios, endpoint.value, {knowledge_base__id: itemsStore.editing})

function addDataSource() {
    dataSources.value.push({})
}

const addingDataSource = computed(() => dataSources.value.length > 0 && dataSources.value[dataSources.value.length - 1].id === undefined)

</script>

<style lang="scss">
.el-collapse {
    width: 100%;
    .el-collapse-item {
        margin-bottom: 24px;
        border-radius: 10px;
        border: 1px solid $chatfaq-color-primary-200;
    }

    .el-collapse-item__header {
        //styleName: Title/XS/Bold;
        border-radius: 10px;
        font-family: Montserrat;
        font-size: 18px;
        font-weight: 700;
        padding: 32px;

    }
}
</style>
