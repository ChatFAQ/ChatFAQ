<template>
    <div class="dashboard-page-title">{{ $t('data') }}</div>
    <el-tabs class="main-page-tabs" @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :label="$t('knowledgebase')" name="knowledge-base">
            <ReadWriteView
                :readableName="$t('knowledgebase')"
                apiUrl="/back/api/language-model/knowledge-bases/"
                :cardProps="{
                    'lang': $t('lang'),
                    'num_of_data_sources': $t('numofdatasources'),
                    'num_of_knowledge_items': $t('numofknowledgeitems'),
                }"
                :tableProps="{
                    'lang': {'name': $t('lang')},
                    'num_of_data_sources': {'name': $t('numofdatasources')},
                    'num_of_knowledge_items': {'name': $t('numofknowledgeitems')},
                }"
                :excludeFields="['num_of_data_sources', 'num_of_knowledge_items']"
            >
                <template v-slot:extra-card-bottom="props">
                    <el-button class="go-to-kis-button" @click="goToKIs(props.item.id)">{{ $t("viewknowledgeitems") }}</el-button>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :label="$t('knowledgeitem')" name="knowledge-item">
            <ReadWriteView :readableName="$t('knowledgeitem')"
                           apiUrl="/back/api/language-model/knowledge-items/"
                           :tableProps="{
                                'title': {'name': $t('title')},
                                'created_date': {'name': $t('created_date')},
                           }"
                           :filtersSchema="[
                               {'type': 'ref', 'placeholder': $t('knowledgebase'), 'field': 'knowledge_base__id', 'endpoint': '/back/api/language-model/knowledge-bases/'},
                               {'type': 'range-date', 'startPlaceholder': $t('startdate'), 'endPlaceholder': $t('enddate'), 'field': 'created_date'},
                               {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
                           ]"
                           requiredFilter="knowledge_base__id"
            >
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import { useItemsStore } from "~/store/items.js";
import Password from "~/components/user_management/fields/Password.vue";

const password = ref(null)

const { $axios } = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("knowledge-base")
await itemsStore.loadSchema($axios)


function goToKIs(kb_id) {
    itemsStore.stateToRead()
    itemType.value = "knowledge-item"
    itemsStore.filters["knowledge_base__id"] = kb_id
}

</script>

<style scoped lang="scss">
.go-to-kis-button {
    @include button-primary;
    width: 100%;
    margin-top: 8px;
}
</style>
