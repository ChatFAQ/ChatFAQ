<template>
    <div class="dashboard-page-title">{{ $t("welcome", {name: ""}) }}</div>
    <div class="dashboard-wrapper" v-loading="itemsStore.loading" element-loading-background="rgba(255, 255, 255, 0.8)">
        <div class="section-title">{{ $t("sdks") }}</div>
        <div class="cards-view">
            <div class="card-wrapper" v-for="sdk in sdks">
                <Card :editable="false" :deletable="false" @click-delete="initItems" :item="sdk"
                      :cardProps="cardPropsSDK" :itemSchema="itemSchemaSDK" :apiUrl="SDKAPIUrl" :titleProps="['fsm_name']"/>
            </div>
        </div>
        <div class="section-title">{{ $t("rags") }}</div>
        <div class="cards-view">
            <div class="card-wrapper" v-for="rag in rags">
                <Card @click-delete="initItems" @click-edit="() => goTo('ai_config')" :item="rag"
                      :cardProps="cardPropsRAG" :itemSchema="itemSchemaRAG" :apiUrl="RAGAPIUrl">
                    <template v-slot:extra-card-bottom="{item}">
                        <el-button class="bottom-card-button" @click="callRagReindex(item.id, $t)"
                                   :disabled="item.disabled || item.index_up_to_date">
                            <span>{{ $t("reindex") }}</span>
                            <el-icon>
                                <Refresh/>
                            </el-icon>
                        </el-button>
                    </template>
                    <template v-slot:enabled="{item, name}">
                        <span class="title">{{ name }}:</span>
                        <el-switch
                            @change="switchDisabled({id: item.id, disabled: item.disabled})"
                            v-model="item.disabled"
                            :active-value="false"
                            :inactive-value="true"
                        />
                    </template>
                </Card>
            </div>
        </div>
        <div class="section-title">{{ $t("widgets") }}</div>
        <div class="cards-view">
            <div class="card-wrapper" v-for="widget in widgets">
                <Card @click-delete="initItems" @click-edit="() => goTo('widget_config')"
                      :item="widget" :cardProps="cardPropsWidget" :itemSchema="itemSchemaWidget" :apiUrl="WidgetAPIUrl"/>
            </div>
        </div>
    </div>
</template>

<script setup>
import {ref} from 'vue'
import {authHeaders, useItemsStore} from "~/store/items.js";
import {useI18n} from "vue-i18n";
import Card from "~/components/generic/Card.vue";
import {callRagReindex} from "~/utils/index.js";

const {t} = useI18n();
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const router = useRouter();

// -------- RAG --------
const RAGAPIUrl = ref("/back/api/language-model/rag-configs/")
const cardPropsRAG = ref({
    'enabled': t('enabled'),
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
async function switchDisabled(val) {
    await itemsStore.upsertItem($axios, RAGAPIUrl.value, val, {limit: 0, offset: 0, ordering: undefined})
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

    .cards-view {
        display: grid;
        flex-wrap: wrap;
        width: 100%;
        justify-items: stretch;
        grid-template-columns: repeat(auto-fill, minmax(100px, 25%));
    }

    .card-wrapper {
        width: 100%;
        padding: 16px;

        .box-card {
            cursor: pointer;

            &:hover {
                box-shadow: 0px 4px 4px 0px #DFDAEA66 !important;
            }
        }
    }
    .bottom-card-button {
        @include button-primary;
        width: 100%;
        margin-top: 8px;
        span {
            margin-right: 8px;
        }
    }
}
</style>
