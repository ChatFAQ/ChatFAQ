<template>
    <div class="page-title">{{ $t("ai_configuration") }}</div>
    <el-tabs v-model="selectedTab" >
        <el-tab-pane :label="$t('retriever')" name="retriever">
            <Retriever/>
        </el-tab-pane>
        <el-tab-pane :label="$t('prompt')" name="prompt"></el-tab-pane>
        <el-tab-pane :label="$t('generation')" name="generation"></el-tab-pane>
        <el-tab-pane :label="$t('llm')" name="llm"></el-tab-pane>
        <el-tab-pane :label="$t('rag')" name="rag"></el-tab-pane>
    </el-tabs>
</template>

<script setup>

import Retriever from "~/components/ai_config/Retriever.vue";
const selectedTab = ref("retriever")

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
