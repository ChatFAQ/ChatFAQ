<template>
    <div class="page-title">A.I. Configuration</div>
    <el-tabs v-model="selectedTab" >
        <el-tab-pane label="Retriever" name="retriever">
            <Retriever/>
        </el-tab-pane>
        <el-tab-pane label="Prompt" name="prompt">Prompt</el-tab-pane>
        <el-tab-pane label="Generation" name="generation">Generation</el-tab-pane>
        <el-tab-pane label="LLM" name="llm">LLM</el-tab-pane>
        <el-tab-pane label="RAG" name="rag">RAG</el-tab-pane>
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
