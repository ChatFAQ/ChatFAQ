<template>
    <div class="dashboard-page-title">{{ $t('data') }}</div>
    <el-tabs @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('knowledgebase')" name="knowledge-base">
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
                    <el-button class="go-to-kis-button">{{ $t("viewknowledgeitems") }}</el-button>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('knowledgeitem')" name="knowledge-item">
            <ReadWriteView :readableName="$t('knowledgeitem')"
                           apiUrl="/back/api/language-model/knowledge-items/"
                           :cardProps="{
                    'title': $t('title'),
                }"
                           :tableProps="{
                    'title': $t('title'),
                }">
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


function submitPassword() {
    password.value.submit()
}
</script>

<style scoped lang="scss">
.go-to-kis-button {
    @include button-primary;
    width: 100%;
    margin-top: 8px;
}
</style>