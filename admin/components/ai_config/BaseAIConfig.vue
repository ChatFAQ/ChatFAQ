<template>
    <div class="page-title">{{ $t("aiconfiguration") }}</div>
    <el-tabs @tab-change="changeUrl" v-model="itemType" >
        <el-tab-pane :label="$t('retriever')" name="retriever-configs">
            <Retriever :edit="id" :add="add"/>
        </el-tab-pane>
        <el-tab-pane :label="$t('prompt')" name="prompt-configs"></el-tab-pane>
        <el-tab-pane :label="$t('generation')" name="generation-configs"></el-tab-pane>
        <el-tab-pane :label="$t('llm')" name="llm-configs"></el-tab-pane>
        <el-tab-pane :label="$t('rag')" name="rag-configs"></el-tab-pane>
    </el-tabs>
</template>

<script setup>
import Retriever from "~/components/ai_config/Retriever.vue";
const route = useRoute()

const itemType = ref(route.params.itemType)
const id = ref(route.params.id)
const add = ref(route.path.endsWith("/add/"))

function changeUrl(tabName) {
    history.pushState({}, null, `/ai_config/${tabName}/`)
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
