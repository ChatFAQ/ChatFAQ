<template>
    <div class="data-sources-wrapper">
        <el-collapse>
            <el-collapse-item v-for="(dataSource, index) in dataSources" :title="$t('datasource', {index})" :name="index">
                <WriteView
                    :readableName="'Data Sources'"
                    :apiUrl="endpoint"
                    :itemId="dataSource.id"
                    :backButton="false"
                    :order="['original_pdf', 'original_csv', 'original_url', 'parser']"
                    :excludeFields="['knowledge_base']"
                >
                </WriteView>
          </el-collapse-item>
          -<div v-if="!addingDataSource" @click="addDataSource">{{ $t('adddatasource') }}</div>-
        </el-collapse>
    </div>
</template>


<script setup>
import WriteView from "~/components/generic/WriteView.vue";
import { useItemsStore } from "~/store/items.js";
const endpoint = ref("/back/api/language-model/data-sources/")
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const dataSources = ref([])
dataSources.value = (await itemsStore.retrieveItems($axios, endpoint.value, {
    limit: 0,
    offset: 0,
    knowledge_base__id: itemsStore.editing
}, false)).results

console.log("------------------------")
console.log(dataSources.value)

function addDataSource() {
    dataSources.value.push({})
}

const addingDataSource = computed(() => dataSources.value.length > 0 && dataSources.value[dataSources.value.length - 1].id === undefined)

</script>

<style lang="scss">
.data-sources-wrapper {
    width: 100%;
    .write-view-wrapper {
        margin: 0;
    }
    .form-section {
        border: none;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .el-collapse {
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
}
</style>
