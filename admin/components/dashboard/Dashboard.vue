<template>
    <div class="dashboard-page-title">{{ $t("welcome", {name: ""}) }}</div>
    <div class="dashboard-wrapper" v-loading="itemsStore.loading" element-loading-background="rgba(255, 255, 255, 0.8)">
        <div class="section-title">{{ $t("sdks") }}</div>
        <div class="cards-wrapper">
            <Card :editable="false" :deletable="false" @click-delete="initItems" class="dashboard-card" v-for="sdk in sdks" :item="sdk" :cardProps="cardPropsSDK" :itemSchema="itemSchemaSDK" :apiUrl="SDKAPIUrl" :titleProps="['fsm_name']">
            </Card>
        </div>
        <div class="section-title">{{ $t("rags") }}</div>
        <div class="cards-wrapper">
            <Card @click-delete="initItems" @click-edit="() => goTo('ai_config')" class="dashboard-card" v-for="rag in rags" :item="rag" :cardProps="cardPropsRAG" :itemSchema="itemSchemaRAG" :apiUrl="RAGAPIUrl">
            </Card>
        </div>
        <div class="section-title">{{ $t("widgets") }}</div>
        <div class="cards-wrapper">
            <Card @click-delete="initItems" @click-edit="() => goTo('widget_config')" class="dashboard-card" v-for="widget in widgets" :item="widget" :cardProps="cardPropsWidget" :itemSchema="itemSchemaWidget" :apiUrl="WidgetAPIUrl">
            </Card>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import {authHeaders, useItemsStore} from "~/store/items.js";
import {useI18n} from "vue-i18n";
import Card from "~/components/generic/Card.vue";

const { t } = useI18n();
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const router = useRouter();

// -------- RAG --------
const RAGAPIUrl = ref("/back/api/language-model/rag-configs/")
const cardPropsRAG = ref({
    'knowledge_base': t('knowledgebase'),
    'llm_config': t('llmconfig'),
    'prompt_config': t('promptconfig'),
    'generation_config': t('generationconfig'),
    'retriever_config': t('retrieverconfig'),
})
const itemSchemaRAG = ref({})

// -------- Widget --------
const WidgetAPIUrl = ref("/back/api/widget/widgets/")
const cardPropsWidget = ref({
    'domain': t('domain'),
    'fsm_def': t('fsmdef'),
})
const itemSchemaWidget = ref({})

// -------- SDK --------
const SDKAPIUrl = ref("/back/api/broker/sdks/")
const cardPropsSDK = ref({
    'created_date': t('created_date')
})
const itemSchemaSDK = ref({})
const rags = ref([])
const widgets = ref([])
const sdks = ref([])

async function initData() {
    itemsStore.loading = true
    itemSchemaRAG.value = await itemsStore.getSchemaDef($axios, RAGAPIUrl.value)
    itemSchemaWidget.value = await itemsStore.getSchemaDef($axios, WidgetAPIUrl.value)
    itemSchemaSDK.value = await itemsStore.getSchemaDef($axios, SDKAPIUrl.value)
    itemsStore.loading = false
}
async function initItems() {
    rags.value = (await $axios.get(RAGAPIUrl.value, {headers: authHeaders()})).data.results
    widgets.value = (await $axios.get(WidgetAPIUrl.value, {headers: authHeaders()})).data.results
    sdks.value = (await $axios.get(SDKAPIUrl.value, {headers: authHeaders()})).data.results
}

await initData()
await initItems()

function goTo(route) {
    router.push({name: route})
}
</script>


<style lang="scss">
.dashboard-wrapper {
    margin-left: 146px;
    margin-right: 160px;
    .section-title {
        font-family: Open Sans;
        font-size: 14px;
        font-weight: 600;
        color: $chatfaq-color-neutral-black;
        margin-bottom: 16px;
        margin-top: 24px;
        margin-left: 16px;
    }
    .cards-wrapper {
        display: grid;
        flex-wrap: wrap;
        width: 100%;
        justify-items: stretch;
        grid-template-columns: repeat(auto-fill, minmax(100px, 350px));
        > .el-card {
            margin: 16px;
        }
    }
}
</style>
