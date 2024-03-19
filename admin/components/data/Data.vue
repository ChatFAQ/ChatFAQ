<template>
    <div class="dashboard-page-title">{{ $t('data') }}</div>
    <el-tabs class="main-page-tabs" @tab-click="itemsStore.stateToRead" v-model="itemType">
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
        <el-tab-pane :label="$t('existingintents')" name="existing_intents">
            <ReadWriteView :readableName="$t('intents')"
                           apiUrl="/back/api/language-model/intents/"
                           :tableProps="{
                                'intent_name': {'name': $t('intentname')},
                                'num_of_knowledge_items': {'name': $t('knowledgeitems')},
                                'name_of_knowledge_base': {'name': $t('nameofknowledgebase')},
                                'intents': {'name': $t('intents')},
                           }"
                           :filtersSchema="[
                               {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
                               {'type': 'ref', 'placeholder': $t('knowledgebase'), 'field': 'knowledge_base__id', 'endpoint': '/back/api/language-model/knowledge-bases/'},
                           ]"
                           :defaultFilters="{'suggested_intent': false}"
                           :textExplanation="$t('intentexplanation')"
                           readOnly
            >
                <template v-slot:intents="{row}">
                    <span class="command-edit" @click="showKIsForIntent(row)">{{ $t("view") }}</span>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :label="$t('suggestedintents')" name="suggested_intents">
            <ReadWriteView :readableName="$t('intents')"
                           apiUrl="/back/api/language-model/intents/"
                           :tableProps="{
                                'intent_name': {'name': $t('intentname')},
                                'num_of_knowledge_items': {'name': $t('knowledgeitems')},
                                'name_of_knowledge_base': {'name': $t('nameofknowledgebase')},
                                'questions': {'name': $t('questions')},
                           }"
                           :filtersSchema="[
                               {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
                               {'type': 'ref', 'placeholder': $t('knowledgebase'), 'field': 'knowledge_base__id', 'endpoint': '/back/api/language-model/knowledge-bases/'},
                           ]"
                           :defaultFilters="{'suggested_intent': true}"
                           :textExplanation="$t('intentexplanation')"
                           readOnly
            >
                <template v-slot:questions="{row}">
                    <span class="command-edit" @click="showQuestionsForIntent(row)">{{ $t("view") }}</span>
                </template>
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="showingIntentRefs" :title="$t('refs')" width="500" center>
        <span>
            1{{intentKisRefs}}2
            <el-table v-if="intentKisRefs"
                      class="table-view"
                      :data="intentKisRefs"
                      :stripe="false"
                      style="width: 100%">
                <el-table-column
                    :prop="'title'"
                    :label="$t('title')"
                    sortable
                />
                <el-table-column
                    :prop="'content'"
                    :label="$t('title')"
                    sortable
                />
                <el-table-column
                    :prop="'url'"
                    :label="$t('title')"
                    sortable
                />
            </el-table>
        </span>
    </el-dialog>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";
import WriteViewDataSources from "~/components/data/WriteViewDataSources.vue";

const password = ref(null)
const intentKIsRefs = ref(undefined)
const intentQuestionsRefs = ref(undefined)
const showingIntentRefs = ref(false)
const itemsStore = useItemsStore()

const itemType = ref("knowledge-base")
const dataSources = ref(null)

await itemsStore.loadSchema()


function goToKIs(kb_id) {
    itemsStore.stateToRead()
    itemsStore.filters = {"knowledge_base__id": kb_id}
    itemType.value = "knowledge-item"
}

async function submitKnowledgeBase(id, form) {
    await dataSources.value.submit(id)
}
async function showKIsForIntent(row) {
    const res = await itemsStore.retrieveItems("/back/api/language-model/knowledge-items/", {"intent__id": row.id, limit: 0, offset: 0, ordering: undefined})
    intentKIsRefs.value = res.results
    intentQuestionsRefs.value = undefined
    showingIntentRefs.value = true
}
async function showQuestionsForIntent(row) {
    const res = await itemsStore.retrieveItems("/back/api/language-model/messages/", {"intent__id": row.id, limit: 0, offset: 0, ordering: undefined})
    intentQuestionsRefs.value = res.results
    intentKIsRefs.value = undefined
    showingIntentRefs.value = true
}
</script>

<style scoped lang="scss">
.bottom-card-button {
    @include button-primary;
    width: 100%;
    margin-top: 8px;
}
</style>
