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
                    'name': {'name': $t('name')},
                    'lang': {'name': $t('lang')},
                    'num_of_data_sources': {'name': $t('numofdatasources')},
                    'num_of_knowledge_items': {'name': $t('numofknowledgeitems')},
                }"
                :excludeFields="['num_of_data_sources', 'num_of_knowledge_items']"
                :textExplanation="$t('knowledgebaseexplanation')"
            >
                <template v-slot:extra-card-bottom="props">
                    <el-button class="bottom-card-button" @click="goToKIs(props.item.id)">{{ $t("viewknowledgeitems") }}</el-button>
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
                           :textExplanation="$t('knowledgeitemexplanation')"
            >
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :label="$t('intents')" name="intents">
            <ReadWriteView :readableName="$t('intents')"
                           apiUrl="/back/api/language-model/intents/"
                           :tableProps="{
                                'intent_name': {'name': $t('intentname')},
                                'num_of_knowledge_items': {'name': $t('numofknowledgeitems')},
                                'name_of_knowledge_base': {'name': $t('nameofknowledgebase')},
                           }"
                           :filtersSchema="[
                               {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
                               {'type': 'ref', 'placeholder': $t('knowledgebase'), 'field': 'knowledge_base__id', 'endpoint': '/back/api/language-model/knowledge-bases/'},
                           ]"
                           :textExplanation="$t('intentexplanation')"
                           readOnly
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
.bottom-card-button {
    @include button-primary;
    width: 100%;
    margin-top: 8px;
}
</style>
