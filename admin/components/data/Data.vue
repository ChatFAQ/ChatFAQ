<template>
    <div class="dashboard-page-title">{{ $t('data') }}</div>
    <el-tabs class="main-page-tabs" @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :label="$t('knowledgebase')" name="knowledge-base">
            <ReadWriteView
                :readableName="$t('knowledgebase')"
                apiUrl="/back/api/language-model/knowledge-bases/"
                :cardProps="{
                    'lang': $t('lang'),
                    'num_of_data_sources': $t('datasources'),
                    'num_of_knowledge_items': $t('knowledgeitems'),
                }"
                :tableProps="{
                    'name': {'name': $t('name')},
                    'lang': {'name': $t('lang')},
                    'num_of_data_sources': {'name': $t('datasources')},
                    'num_of_knowledge_items': {'name': $t('knowledgeitems')},
                }"
                :excludeFields="['num_of_data_sources', 'num_of_knowledge_items']"
                :textExplanation="$t('knowledgebaseexplanation')"
                :filtersSchema="[
                   {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
               ]"
                :leaveAfterSave="false"
                @submitFormEnd="submitKnowledgeBase"
            >
                <template v-slot:extra-card-bottom="{item}">
                    <el-button class="bottom-card-button" @click="goToKIs(item.id)">{{
                            $t("viewknowledgeitems")
                        }}
                    </el-button>
                </template>
                <template v-slot:extra-write-bottom>
                    <WriteViewDataSources :itemType="itemType" ref="dataSources"/>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :label="$t('knowledgeitem')" name="knowledge-item">
            <ReadWriteView :readableName="$t('knowledgeitem')"
                           apiUrl="/back/api/language-model/knowledge-items/"
                           :tableProps="{
                                'title': {'name': $t('title')},
                                'created_date': {'name': $t('created_date')},
                                'knowledge_base': {'name': $t('knowledgebase')},
                           }"
                           :filtersSchema="[
                               {'type': 'ref', 'placeholder': $t('knowledgebase'), 'field': 'knowledge_base__id', 'endpoint': '/back/api/language-model/knowledge-bases/'},
                               {'type': 'range-date', 'startPlaceholder': $t('startdate'), 'endPlaceholder': $t('enddate'), 'field': 'created_date'},
                               {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
                           ]"
                           :textExplanation="$t('knowledgeitemexplanation')"
            >
                <template v-slot:write-content="{fieldName, form, formServerErrors}">
                    <el-form-item :label="$t(fieldName)"
                                  :prop="fieldName"
                                  :error="formServerErrors[fieldName]">
                        <el-input
                            class="system-prefix-input"
                            v-model="form[fieldName]"
                            autosize
                            @keydown.enter.stop
                            type="textarea"
                        />
                    </el-form-item>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :label="$t('intents')" name="intents">
            <ReadWriteView :readableName="$t('intents')"
                           apiUrl="/back/api/language-model/intents/"
                           :tableProps="{
                                'intent_name': {'name': $t('intentname')},
                                'num_of_knowledge_items': {'name': $t('knowledgeitems')},
                                'name_of_knowledge_base': {'name': $t('nameofknowledgebase')},
                           }"
                           :filtersSchema="[
                               {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
                               {'type': 'ref', 'placeholder': $t('knowledgebase'), 'field': 'knowledge_base__id', 'endpoint': '/back/api/language-model/knowledge-bases/'},
                           ]"
                           :textExplanation="$t('intentexplanation')"
                           readOnly
            >
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";
import WriteViewDataSources from "~/components/data/WriteViewDataSources.vue";

const password = ref(null)

const {$axios} = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("knowledge-base")
const dataSources = ref(null)

await itemsStore.loadSchema($axios)


function goToKIs(kb_id) {
    itemsStore.stateToRead()
    itemType.value = "knowledge-item"
    itemsStore.filters["knowledge_base__id"] = kb_id
}

async function submitKnowledgeBase(id, form) {
    await dataSources.value.submit(id)
}
</script>

<style scoped lang="scss">
.bottom-card-button {
    @include button-primary;
    width: 100%;
    margin-top: 8px;
}
</style>
