<template>
    <div class="dashboard-page-title">{{ $t("welcome", {name: ""}) }}</div>
    <div class="dashboard-wrapper" v-loading="itemsStore.loading" element-loading-background="rgba(255, 255, 255, 0.8)">
        <div class="section-title">{{ $t("sdks") }}</div>
        {{sdks}}
        <div class="section-title">{{ $t("rags") }}</div>
        {{rags}}
        <div class="section-title">{{ $t("widgets") }}</div>
        {{widgets}}

    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import {authHeaders, useItemsStore} from "~/store/items.js";
import Filters from "~/components/generic/filters/Filters.vue";
import {useI18n} from "vue-i18n";

const { t } = useI18n();
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();

const rags = (await $axios.get("/back/api/language-model/rag-configs/",{headers: authHeaders()})).data
const widgets = (await $axios.get("/back/api/widget/widgets/",{headers: authHeaders()})).data
const sdks = (await $axios.get("/back/api/broker/sdks/",{headers: authHeaders()})).data

</script>

<style lang="scss">
</style>

<style lang="scss" scoped>
.dashboard-wrapper {
    .section-title {
        font-family: Open Sans;
        font-size: 14px;
        font-weight: 600;
        color: $chatfaq-color-neutral-black;
        margin-bottom: 16px;
        margin-top: 26px;
    }
}
</style>
