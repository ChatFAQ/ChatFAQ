<template>
    <div class="data-sources-wrapper">
        <el-collapse>
            <el-collapse-item v-for="(dataSource, index) in dataSources" :title="$t('datasource', {index})" :name="index">
                <WriteView
                    :readableName="'Data Sources'"
                    :apiUrl="endpoint"
                    :itemId="dataSource.id"
                    :backButton="false"
                    :commandButtons="false"
                    :leaveAfterSave="false"
                    :order="['original_pdf', 'original_csv', 'original_url', 'parser']"
                    :excludeFields="['knowledge_base']"
                    ref="dataSourceForms"
                >
                </WriteView>
          </el-collapse-item>
        </el-collapse>
        <div ref="xxx" class="add-new-data-source-button" @click="addDataSource">{{ $t('addnewdatasource') }}</div>
    </div>
</template>


<script setup>
import {ref, defineExpose} from "vue";
import WriteView from "~/components/generic/WriteView.vue";
import { useItemsStore } from "~/store/items.js";
const endpoint = ref("/back/api/language-model/data-sources/")
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const dataSources = ref([])
const dataSourceForms = ref(null)

defineExpose({submit})

if (itemsStore.editing) {
    dataSources.value = (await itemsStore.retrieveItems($axios, endpoint.value, {
        limit: 0,
        offset: 0,
        knowledge_base__id: itemsStore.editing
    }, false)).results
}

function addDataSource() {
    dataSources.value.push({})
}
async function submit(kbId) {
    let success = true
    for (let i = 0; i < dataSourceForms.value.length; i++) {
        if (dataSourceForms.value[i]) {
            const _success = await dataSourceForms.value[i].submitForm({knowledge_base: kbId})
            if (!_success)
                success = _success
        }
    }
    if (success) {
        // itemsStore.stateToRead()
    }
}

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
    .add-new-data-source-button {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        width: 100%;
        padding: 10px;
        margin-bottom: 24px;
        color: $chatfaq-color-primary-500;
        border: 1px dashed $chatfaq-color-primary-500;
        border-radius: 10px;
        cursor: pointer;
    }
}
</style>
