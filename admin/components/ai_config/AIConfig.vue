<template>
    <div class="dashboard-page-title">{{ $t("aiconfiguration") }}</div>
    <el-tabs class="main-page-tabs" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('llm')" name="llm-configs">
            <ReadWriteView :readableName="$t('llm')" apiUrl="/back/api/language-model/llm-configs/"
                           :cardProps="{
                    'llm_type': $t('llmtype'),
                    'llm_name': $t('llmname'),
                    'base_url': $t('baseurl'),
                    'model_max_length': $t('modelMaxLength'),
                    'enabled': $t('enabled'),
                    'num_replicas': $t('numreplicas'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'llm_type': {'name': $t('llmtype')},
                    'llm_name': {'name': $t('llmname')},
                    'enabled': {'name': $t('enabled')},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}">
                <template v-slot:write-api_key="props">
                    <SecretInput :form="props.form" fieldName="api_key" placeholder="Please input API Key"/>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane v-if="$useRay" :lazy="true" :label="$t('retriever')" name="retriever-configs">
            <ReadWriteView :readableName="$t('retriever')" apiUrl="/back/api/language-model/retriever-configs/"
                           :cardProps="{
                    'model_name': $t('modelname'),
                    'retriever_type': $t('retrievertype'),
                    'knowledge_base': $t('knowledgebase'),
                    'batch_size': $t('batchsize'),
                    'device': $t('device'),
                    'enabled': $t('enabled'),
                    'num_replicas': $t('numreplicas'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'model_name': {'name': $t('modelname')},
                    'knowledge_base': {'name': $t('knowledgebase')},
                    'retriever_type': {'name': $t('retrievertype')},
                    'device': {'name': $t('device')},
                    'enabled': {'name': $t('enabled')},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}"
                >
                <template v-slot:extra-card-bottom="{item}">
                    <el-button class="bottom-card-button" @click="callRetrieverReindex(item.id, $t)"
                            :disabled="item.index_status === 'up_to_date'">
                        <span>{{ $t("reindex") }}</span>
                        <el-icon>
                            <Refresh/>
                        </el-icon>
                    </el-button>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('prompt')" name="prompt-configs">
            <ReadWriteView :readableName="$t('prompt')" apiUrl="/back/api/language-model/prompt-configs/"
                           :cardProps="{}"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'updated_date': {'name': $t('updateddate'), 'sortable': true},
                }"
                :defaultSort="{'prop': 'name'}">
                <template v-slot:write-prompt="{fieldName, form, formServerErrors}">
                    <el-form-item :label="$t(fieldName)"
                                  :prop="fieldName"
                                  :error="formServerErrors[fieldName]">
                        <el-input
                            class="prompt-input"
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
                    'seed': $t('seed'),
                }"
                           :tableProps="{
                    'name': {'name': $t('name'), 'sortable': true},
                    'temperature': {'name': $t('temperature')},
                    'max_tokens': {'name': $t('maxtokens')},
                    'seed': {'name': $t('seed')},
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
import {callRetrieverReindex} from "~/utils/index.js";
import SecretInput from "~/components/generic/fields/SecretInput.vue";

const {$axios} = useNuxtApp();
const itemsStore = useItemsStore()
const itemType = ref("llm-configs")
await itemsStore.loadSchema()
const { $useRay } = useNuxtApp()

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