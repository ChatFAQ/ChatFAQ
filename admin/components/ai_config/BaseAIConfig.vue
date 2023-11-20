<template>
  <div class="page-title">{{ $t("aiconfiguration") }}</div>
  <el-tabs @tab-change="changeUrl" v-model="itemType">
    <el-tab-pane :lazy="true" :label="$t('retriever')" name="retriever-configs">
      <ReadWriteView apiName="retriever-configs" itemName="retriever" schemaName="RetrieverConfig"
                     :cardProps="{
                    'name': $t('name'),
                    'model_name': $t('modelname'),
                    'device': $t('device'),
                }"
                     :tableProps="{
                    'name': $t('name'),
                    'model_name': $t('modelname'),
                    'device': $t('device'),
                    'updated_date': $t('updateddate'),
                }">
      </ReadWriteView>
    </el-tab-pane>
    <el-tab-pane :lazy="true" :label="$t('prompt')" name="prompt-configs">
      <ReadWriteView apiName="prompt-configs" itemName="prompt" schemaName="PromptConfig"
                     :cardProps="{
                    'name': $t('name'),
                    'n_contexts_to_use': $t('contextsnumber'),
                }"
                     :tableProps="{
                    'name': $t('name'),
                    'n_contexts_to_use': $t('contextsnumber'),
                    'updated_date': $t('updateddate'),
                }">
      </ReadWriteView>
    </el-tab-pane>
    <el-tab-pane :lazy="true" :label="$t('generation')" name="generation-configs">
      <ReadWriteView apiName="generation-configs" itemName="generation"
                     schemaName="GenerationConfig"
                     :cardProps="{
                    'name': $t('name'),
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
      <ReadWriteView apiName="llm-configs" itemName="LLM" schemaName="LLMConfig"
                     :cardProps="{
                    'name': $t('name'),
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
      <ReadWriteView apiName="rag-configs" itemName="RAG" schemaName="RAGConfig"
                     :cardProps="{
                    'name': $t('name'),
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

const route = useRoute();
const router = useRouter();

const itemType = ref(route.params.itemType)

function changeUrl(tabName) {
  router.push({
    path: `/ai_config/${tabName}/`,
  });
}

</script>

<style scoped lang="scss">
.page-title {
  //styleName: Title/XS/Bold;
  font-size: 18px;
  font-weight: 700;
  line-height: 22px;
  letter-spacing: 0em;
  text-align: left;
  margin-bottom: 16px;
}
</style>
