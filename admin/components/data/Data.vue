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
                           ref="suggestedIntentsView"
                           readOnly
            >
                <template v-slot:intents="{row}">
                    <span class="command-edit" @click="showKIsForIntent(row.id)">{{ $t("view") }}</span>
                </template>
                <template v-slot:extra-actions>
                    <el-button class="extra-command" round plain @click="generateIntents(suggestedIntentsView?.readView?.filtersEl?.filters?.knowledge_base__id)" :disabled="suggestedIntentsView?.readView?.filtersEl?.filters?.knowledge_base__id === undefined">
                        <span v-if="suggestedIntentsView?.readView?.filtersEl?.filters?.knowledge_base__id === undefined">{{ $t("selectaknowledgebase") }}</span>
                        <span v-else>{{ $t("generateintents") }}</span>
                    </el-button>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :label="$t('suggestedintents')" name="suggested_intents">
            <ReadWriteView :readableName="$t('intents')"
                           apiUrl="/back/api/language-model/intents/"
                           :tableProps="{
                                'intent_name': {'name': $t('intentname')},
                                'num_of_messages': {'name': $t('messages')},
                                'messages': {'name': $t('messages')},
                           }"
                           :filtersSchema="[
                               {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
                               {'type': 'ref', 'placeholder': $t('knowledgebase'), 'field': 'knowledge_base__id', 'endpoint': '/back/api/language-model/knowledge-bases/'},
                           ]"
                           :defaultFilters="{'suggested_intent': true}"
                           :textExplanation="$t('intentexplanation')"
                           ref="generatedIntentsView"
                           readOnly
            >
                <template v-slot:messages="{row}">
                    <span class="command-edit" @click="showMessagesForIntent(row.id)">{{ $t("view") }}</span>
                </template>
                <template v-slot:extra-actions>
                    <el-button class="extra-command" round plain @click="suggestIntents(generatedIntentsView?.readView?.filtersEl?.filters?.knowledge_base__id)" :disabled="generatedIntentsView?.readView?.filtersEl?.filters?.knowledge_base__id === undefined">
                        <span v-if="generatedIntentsView?.readView?.filtersEl?.filters?.knowledge_base__id === undefined">{{ $t("selectaknowledgebase") }}</span>
                        <span v-else>{{ $t("suggestintents") }}</span>
                    </el-button>
                </template>
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="showingIntentRefs" :title="$t(intentKIsRefs ? 'knowledgeitems' : 'messages')" width="750" center>
        <el-table v-if="intentKIsRefs"
                  class="table-view"
                  :data="intentKIsRefs"
                  :stripe="false"
                  style="width: 100%">
            <el-table-column
                prop="title"
                :label="$t('title')"
                sortable
            />
            <el-table-column
                prop="content"
                :label="$t('content')"
            />
        </el-table>
        <el-table if="intentKIsRefs"
                  class="table-view"
                  :data="intentMessagesRefs"
                  :stripe="false"
                  style="width: 100%">
            <el-table-column
                prop="message"
                :label="$t('message')"
                sortable
            />
        </el-table>
    </el-dialog>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";
import WriteViewDataSources from "~/components/data/WriteViewDataSources.vue";
import {ElNotification} from 'element-plus'
import {useI18n} from "vue-i18n";
import {authHeaders} from "~/store/items.js";

const intentKIsRefs = ref(undefined)
const intentMessagesRefs = ref(undefined)
const showingIntentRefs = ref(false)
const itemsStore = useItemsStore()

const itemType = ref("knowledge-base")
const dataSources = ref(null)
const { t } = useI18n();
const { $axios } = useNuxtApp();
const generatedIntentsView = ref(undefined)
const suggestedIntentsView = ref(undefined)

await itemsStore.loadSchema()


function goToKIs(kb_id) {
    itemsStore.stateToRead()
    itemsStore.filters = {"knowledge_base__id": kb_id}
    itemType.value = "knowledge-item"
}

async function submitKnowledgeBase(id, form) {
    await dataSources.value.submit(id)
}
async function showKIsForIntent(IntentId) {
    const res = await itemsStore.retrieveItems("/back/api/language-model/knowledge-items/", {"intent__id": IntentId, limit: 0, offset: 0, ordering: undefined})
    intentKIsRefs.value = res.results
    intentMessagesRefs.value = undefined
    showingIntentRefs.value = true
}
async function showMessagesForIntent(IntentId) {
    const res = await itemsStore.retrieveItems("/back/api/broker/messages/", {"intent__id": IntentId, limit: 0, offset: 0, ordering: undefined})
    intentMessagesRefs.value = res.results.map(res =>
        res.stack && res.stack.length ? {message: res.stack[0].payload} : {message: ""}
    )
    intentKIsRefs.value = undefined
    showingIntentRefs.value = true
}
async function generateIntents(knowledgeBaseId) {
    await _triggerIntentsTask(`/back/api/language-model/intents/${knowledgeBaseId}/generate-intents/?generate_titles=1`)
}
async function suggestIntents(knowledgeBaseId) {
    await _triggerIntentsTask(`/back/api/language-model/intents/${knowledgeBaseId}/suggest-intents/?generate_titles=1`)

}
async function _triggerIntentsTask(endpoint) {
    try {
        await $axios.post(endpoint, {}, {'headers': authHeaders()})
    } catch (e) {
        ElNotification({
            title: t("error"),
            message: t("errorgeneratingitents"),
            type: "error",
        })
        throw e
    }
    ElNotification({
        title: t("success"),
        message: t("intentsgenerated"),
        type: "success",
    })
}
</script>
<style lang="scss">
.el-dialog__header {
    padding-left: 25px;
}
</style>
<style scoped lang="scss">
.bottom-card-button {
    @include button-primary;
    width: 100%;
    margin-top: 8px;
}
.extra-command {
    @include button-round;
}
</style>
