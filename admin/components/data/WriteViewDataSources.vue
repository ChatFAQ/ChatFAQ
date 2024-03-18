<template>
    <div class="data-sources-wrapper">
        <el-collapse>
            <el-collapse-item v-for="(dataSource, index) in dataSources" :key="dataSource.id || dataSource.fakeId" :name="index">
                <WriteView
                    :readableName="'Data Sources'"
                    :apiUrl="endpoint"
                    :itemId="dataSource.id"
                    :backButton="false"
                    :commandButtons="false"
                    :leaveAfterSave="false"
                    :order="['original_pdf', 'original_csv', 'original_url', 'parser']"
                    :excludeFields="['knowledge_base']"
                    :conditionalIncludedFields="{
                        'original_pdf': [
                            'parser',
                            'strategy',
                            'splitter',
                            'chunk_size',
                            'chunk_overlap'
                        ],
                        'original_csv': [
                            'parser',
                            'csv_header',
                            'title_index_col',
                            'content_index_col',
                            'url_index_col',
                            'section_index_col',
                            'role_index_col',
                            'page_number_index_col'
                        ],
                        'original_url': [
                            'parser',
                            'recursive',
                            'splitter',
                            'chunk_size',
                            'chunk_overlap'
                        ]
                    }"
                    ref="dataSourceForms"
                >
                </WriteView>
                <template #title>
                    <div class="tab-title">
                        <div>{{ getTabName(index) }} </div>
                        <el-icon :size="14" @click="setDeleteDataSource(dataSource.id, index)" @click.stop>
                            <Delete/>
                        </el-icon>
                    </div>
                </template>
          </el-collapse-item>
        </el-collapse>
        <div class="add-new-data-source-button" @click="addDataSource">{{ $t('addnewdatasource') }}</div>
    </div>
    <el-dialog v-model="deleteDialogVisible" :title="$t('warning')" width="500" center>
        <span>
            {{ $t('deleteitemwarning') }}
        </span>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="() => {deleteDialogVisible = false}">{{ $t('cancel') }}</el-button>
                <el-button type="primary" @click="deleteDataSource">
                    {{ $t('confirm') }}
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>


<script setup>
import {ref, defineExpose} from "vue";
import WriteView from "~/components/generic/WriteView.vue";
import { useItemsStore } from "~/store/items.js";

import {useI18n} from "vue-i18n";
const { t } = useI18n();

const endpoint = ref("/back/api/language-model/data-sources/")
const itemsStore = useItemsStore()
const dataSources = ref([])
const dataSourceForms = ref(null)
const deleteDialogVisible = ref(false)
const deletingDataSourceID = ref(undefined)
const deletingIndex = ref(undefined)

defineExpose({submit})

if (itemsStore.editing) {
    dataSources.value = (await itemsStore.retrieveItems(endpoint.value, {
        limit: 0,
        offset: 0,
        knowledge_base__id: itemsStore.editing
    }, false)).results
}

function getNameFromFile(file) {
    if (typeof file === "string")
        return file.split("/").pop().split("?").shift()
    return file.name.split("/").pop().split("?").shift()
}

function getTabName(index) {
    if (!dataSourceForms.value || !dataSourceForms.value[index] || !dataSourceForms.value[index].form)
        return t("newdatasource")

    if (dataSourceForms.value[index].form["original_pdf"])
        return getNameFromFile(dataSourceForms.value[index].form["original_pdf"])
    if (dataSourceForms.value[index].form["original_csv"])
        return getNameFromFile(dataSourceForms.value[index].form["original_csv"])
    if (dataSourceForms.value[index].form["original_url"])
        return dataSourceForms.value[index].form["original_url"]
    return t("newdatasource")
}

function addDataSource() {
    dataSources.value.push({fakeId: Math.random()})
}
async function submit(kbId) {
    let success = true

    let totalDSForms = dataSourceForms.value.length
    function successCB(success) {
        if (success)
            totalDSForms--
        if (totalDSForms === 0)
            itemsStore.stateToRead()
    }
    for (let i = 0; i < dataSourceForms.value.length; i++) {
        if (dataSourceForms.value[i]) {
            const _success = await dataSourceForms.value[i].submitForm({knowledge_base: kbId}, successCB)
            if (!_success)
                success = _success
        }
    }
}
function setDeleteDataSource(id, index) {
    deletingDataSourceID.value = id
    deletingIndex.value = index
    deleteDialogVisible.value = true
}
async function deleteDataSource() {
    if(deletingDataSourceID.value !== undefined) {
        await itemsStore.deleteItem(endpoint.value, deletingDataSourceID.value, false)
        dataSources.value.splice(deletingIndex.value, 1)
        deleteDialogVisible.value = false
    }
    else {
        dataSources.value.splice(deletingIndex.value, 1)
        deleteDialogVisible.value = false
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
        border: none !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    .el-collapse {
        .el-collapse-item {
            margin-bottom: 24px;
            border-radius: 10px;
            border: 1px solid $chatfaq-color-primary-200;
            border-radius: 10px;
        }

        .el-collapse-item__header {
            //styleName: Title/XS/Bold;
            font-family: Montserrat;
            font-size: 18px;
            font-weight: 700;
            padding: 32px;
            border-radius: 10px;
            &.is-active {
                border-radius: 10px 10px 0px 0px;
            }

        }
        .el-collapse-item__content {
            padding-bottom: 0px !important;
        }
        .el-collapse-item__wrap {
            border-radius: 0px 0px 10px 10px !important;
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
    .tab-title {
        display: flex;
        justify-content: space-between;
        width: 100%;
        i {
            margin-right: 24px;
            color: $chatfaq-color-primary-500;
        }
    }
    .el-collapse-item__arrow {
        font-size: 16px;

    }
}
</style>
