<template>
    <div class="dashboard-page-title">{{ $t("aiconfiguration") }}</div>
    <el-tabs class="main-page-tabs" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('rag')" name="rag-configs">
            <ReadWriteView :readableName="$t('rag')" apiUrl="/back/api/language-model/rag-configs/"
                           :cardProps="{
                    'knowledge_base': $t('knowledgebase'),
                    'llm_config': $t('llmconfig'),
                    'prompt_config': $t('promptconfig'),
                    'generation_config': $t('generationconfig'),
                    'retriever_config': $t('retrieverconfig'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'knowledge_base': {'name': $t('knowledgebase')},
                    'llm_config': {'name': $t('llmconfig')},
                    'prompt_config': {'name': $t('promptconfig')},
                    'generation_config': {'name': $t('generationconfig')},
                    'retriever_config': {'name': $t('retrieverconfig')},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}">
                <template v-slot:extra-card-bottom="{item}">
                    <el-button class="bottom-card-button" @click="callRagReindex(item.id, $t)"
                            :disabled="item.index_status === 'up_to_date'">
                        <span>{{ $t("reindex") }}</span>
                        <el-icon>
                            <Refresh/>
                        </el-icon>
                    </el-button>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('retriever')" name="retriever-configs">
            <ReadWriteView :readableName="$t('retriever')" apiUrl="/back/api/language-model/retriever-configs/"
                           :cardProps="{
                    'model_name': $t('modelname'),
                    'device': $t('device'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'model_name': {'name': $t('modelname')},
                    'device': {'name': $t('device')},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}">
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('prompt')" name="prompt-configs">
            <ReadWriteView :readableName="$t('prompt')" apiUrl="/back/api/language-model/prompt-configs/"
                           :cardProps="{
                    'n_contexts_to_use': $t('contextsnumber'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'n_contexts_to_use': {'name': $t('contextsnumber')},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}">
                <template v-slot:write-system_prompt="{fieldName, form, formServerErrors}">
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
        <el-tab-pane :lazy="true" :label="$t('generation')" name="generation-configs">
            <ReadWriteView :readableName="$t('generation')" apiUrl="/back/api/language-model/generation-configs/"
                           :cardProps="{
                    'temperature': $t('temperature'),
                    'max_tokens': $t('maxtokens'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'temperature': {'name': $t('temperature')},
                    'max_tokens': {'name': $t('maxtokens')},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}">
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('llm')" name="llm-configs">
            <ReadWriteView :readableName="$t('llm')" apiUrl="/back/api/language-model/llm-configs/"
                           :cardProps="{
                    'llm_type': $t('llmtype'),
                    'llm_name': $t('llmname'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'llm_type': {'name': $t('llmtype')},
                    'llm_name': {'name': $t('llmname')},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}">
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";
import {useI18n} from "vue-i18n";
import {callRagReindex} from "~/utils/index.js";

const {$axios} = useNuxtApp();
const itemsStore = useItemsStore()
const itemType = ref("rag-configs")
await itemsStore.loadSchema()

</script>

<style scoped lang="scss">
.bottom-card-button {
    @include button-primary;
    width: 100%;
    margin-top: 8px;
    span {
        margin-right: 8px;
    }
}
</style>