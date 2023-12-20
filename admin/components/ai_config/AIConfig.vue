<template>
    <div class="dashboard-page-title">{{ $t("aiconfiguration") }}</div>
    <el-tabs @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('retriever')" name="retriever-configs">
            <ReadWriteView :readableName="$t('retriever')" apiUrl="/back/api/language-model/retriever-configs/"
                           :cardProps="{
                    'model_name': $t('modelname'),
                    'device': $t('device'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name')},
                    'model_name': {'name': $t('modelname')},
                    'device': {'name': $t('device')},
                    'updated_date': {'name': $t('updateddate')},
                }">
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('prompt')" name="prompt-configs">
            <ReadWriteView :readableName="$t('prompt')" apiUrl="/back/api/language-model/prompt-configs/"
                           :cardProps="{
                    'n_contexts_to_use': $t('contextsnumber'),
                }"
                           :tableProps="{
                    'name': $t('name'),
                    'n_contexts_to_use': $t('contextsnumber'),
                    'updated_date': $t('updateddate'),
                }">
                <template v-slot:write-system_prefix="{fieldName, form, formServerErrors}">
                    <el-form-item :label="$t(fieldName)"
                                  :prop="fieldName"
                                  :error="formServerErrors[fieldName]">
                        <el-input
                            class="system-prefix-input"
                            v-model="form[fieldName]"
                            autosize
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
                    'max_new_tokens': $t('maxtokens'),
                }"
                           :tableProps="{
                    'name': $t('name'),
                    'temperature': $t('temperature'),
                    'max_new_tokens': $t('maxtokens'),
                    'updated_date': $t('updateddate'),
                }">
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('llm')" name="llm-configs">
            <ReadWriteView :readableName="$t('llm')" apiUrl="/back/api/language-model/llm-configs/"
                           :cardProps="{
                    'llm_type': $t('llmtype'),
                    'llm_name': $t('llmname'),
                }"
                           :tableProps="{
                    'name': $t('name'),
                    'llm_type': $t('llmtype'),
                    'llm_name': $t('llmname'),
                    'updated_date': $t('updateddate'),
                }">
            </ReadWriteView>
        </el-tab-pane>
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
                    'name': $t('name'),
                    'knowledge_base': $t('knowledgebase'),
                    'llm_config': $t('llmconfig'),
                    'prompt_config': $t('promptconfig'),
                    'generation_config': $t('generationconfig'),
                    'retriever_config': $t('retrieverconfig'),
                    'updated_date': $t('updateddate'),
                }">
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";

const {$axios} = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("retriever-configs")
await itemsStore.loadSchema($axios)


</script>

<style lang="scss" scoped>
.system-prefix-input {
}
</style>
