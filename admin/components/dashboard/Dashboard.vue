<template>
    <div class="dashboard-page-title">{{ $t("welcome", { name: userName }) }}</div>
    <div class="dashboard-wrapper" v-loading="itemsStore.loading" element-loading-background="rgba(255, 255, 255, 0.8)">
        <div class="text-explanation" v-html="$t('dashboardexplanation')"></div>
        <div class="section-title">{{ $t("sdks") }}</div>
        <div class="cards-view">
            <div class="no-items" v-if="!sdks || !sdks.length">{{ $t('nosdks') }}</div>
            <Card v-for="sdk in sdks" :editable="false" :deletable="false" @delete="initItems" :item="sdk"
                  :cardProps="cardPropsSDK" :itemSchema="itemSchemaSDK" :apiUrl="SDKAPIUrl"
                  :titleProps="['fsm_name']" />
        </div>
        <div class="section-title">{{ $t("rags") }}</div>
        <div class="cards-view">
            <div class="no-items" v-if="!rags || !rags.length">{{ $t('norags') }}</div>
            <Card v-for="rag in rags" @delete="initItems" @edit="() => goTo('ai_config')" :item="rag"
                  :cardProps="cardPropsRAG" :itemSchema="itemSchemaRAG" :apiUrl="RAGAPIUrl">
                <template v-slot:extra-card-bottom="{item}">
                    <el-button class="bottom-card-button" @click="callRagReindex(item.id, $t)"
                               :disabled="item.index_status === 'up_to_date'">
                        <span>{{ $t("reindex") }}</span>
                        <el-icon>
                            <Refresh />
                        </el-icon>
                    </el-button>
                </template>
                <template v-slot:enabled="{item, name}">
                    <span class="title">{{ name }}:</span>
                    <el-switch
                        v-model="item.enabled"
                        :before-change="() => switchEnabled(item)"
                        @click.native.stop
                        :loading="loading[item.id]"
                        :active-value="true"
                        :inactive-value="false"
                    />
                </template>
            </Card>
        </div>
        <div class="section-title">{{ $t("widgets") }}</div>
        <div class="cards-view">
            <div class="no-items" v-if="!widgets || !widgets.length">{{ $t('nowidgets') }}</div>
            <Card v-for="widget in widgets" @delete="initItems" @edit="() => goTo('widget_config')"
                  :item="widget" :cardProps="cardPropsWidget" :itemSchema="itemSchemaWidget" :apiUrl="WidgetAPIUrl" />
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import { authHeaders, useItemsStore } from "~/store/items.js";
import { useAuthStore } from "~/store/auth.js";
import { useI18n } from "vue-i18n";
import Card from "~/components/generic/Card.vue";
import { callRagReindex, upsertItem } from "~/utils/index.js";

const { t } = useI18n();
const itemsStore = useItemsStore();
const authStore = useAuthStore();
const { $axios } = useNuxtApp();
const router = useRouter();

const loading = ref({});

// -------- RAG --------
const RAGAPIUrl = ref("/back/api/language-model/rag-configs/");
const cardPropsRAG = ref({
    "enabled": t("enabled"),
});
const itemSchemaRAG = ref({});

// -------- Widget --------
const WidgetAPIUrl = ref("/back/api/widget/widgets/");
const cardPropsWidget = ref({
    "domain": t("domain"),
    "fsm_def": t("fsmdef"),
});
const itemSchemaWidget = ref({});

// -------- SDK --------
const SDKAPIUrl = ref("/back/api/broker/sdks/");
const cardPropsSDK = ref({
    "created_date": t("created_date"),
});
const itemSchemaSDK = ref({});
const rags = ref([]);
const widgets = ref([]);
const sdks = ref([]);
const userName = await authStore.getUserName()
async function initData() {
    itemsStore.loading = true;
    itemSchemaRAG.value = await itemsStore.getSchemaDef(RAGAPIUrl.value);
    itemSchemaWidget.value = await itemsStore.getSchemaDef(WidgetAPIUrl.value);
    itemSchemaSDK.value = await itemsStore.getSchemaDef(SDKAPIUrl.value);
    itemsStore.loading = false;
}

async function initItems() {
    rags.value = (await $axios.get(RAGAPIUrl.value + "?enabled=1", { headers: authHeaders() })).data.results;
    widgets.value = (await $axios.get(WidgetAPIUrl.value, { headers: authHeaders() })).data.results;
    sdks.value = (await $axios.get(SDKAPIUrl.value, { headers: authHeaders() })).data.results;
}

await initData();
await initItems();

function goTo(route) {
    router.push({ name: route });
}

async function switchEnabled(item) {
    try {
        loading.value[item.id] = true;
        const res = await upsertItem(RAGAPIUrl.value, { id: item.id, enabled: !item.enabled }, itemsStore, false, {}, t);
        item.enabled = res.enabled;  // Assuming the backend responds with the updated state
        loading.value[item.id] = false;
    } catch (e) {
        loading.value[item.id] = false;
        console.error(e);
    }
}

</script>


<style lang="scss">
.dashboard-wrapper {
    margin-left: 146px;
    margin-right: 160px;
    margin-top: 32px;

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

    .bottom-card-button {
        @include button-primary;
        width: 100%;
        margin-top: 8px;

        span {
            margin-right: 8px;
        }
    }
    .no-items {
        padding: 16px;
    }
}
.text-explanation {
    margin-right: 16px;
    margin-left: 16px;
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    padding-left: 18px;
    border-left: 2px solid $chatfaq-color-primary-500;

}
</style>
