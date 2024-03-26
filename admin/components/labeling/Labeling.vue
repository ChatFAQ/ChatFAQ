<template>
    <div class="dashboard-page-title alone">{{ $t('labeling') }}</div>
    <div class="labeling-wrapper" v-loading="loading" element-loading-background="rgba(255, 255, 255, 0.8)">
    <div class="text-explanation" v-html="$t('labelingexplanation')"></div>
    <ReadWriteView
        v-if="itemsStore.editing === undefined"
        :readableName="$t('conversation')"
        apiUrl="/back/api/broker/conversations/"
        :tableProps="{
            'name': {'name': $t('name')},
            'rags': {'name': $t('rags')},
            'created_date': {'name': $t('created_date'), 'sortable': true},
            'user_id': {'name': $t('userid')},
            'view': {'name': '', 'width': $t('view').length * 20, 'align': 'center'},
        }"
        :defaultSort="{'prop': 'created_date', 'order': 'descending'}"
        :filtersSchema="[
            {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
            {'type': 'range-date', 'startPlaceholder': $t('startdate'), 'endPlaceholder': $t('enddate'), 'field': 'created_date'},
            {'type': 'ref', 'placeholder': $t('rag'), 'field': 'rag', 'endpoint': '/back/api/language-model/rag-configs/'},
            {
                'type': 'enum',
                'placeholder': $t('reviewed'),
                'field': 'reviewed',
                'choices': [{'value': 'completed', 'label': $t('completed')}, {'value': 'pending', 'label': $t('pending')}]
            },
        ]"
        read-only
    >
        <template v-slot:view="{row}">
            <div class="go-to-view" @click="goToLabelingConversation(row.id)">{{ $t("view") }}</div>
        </template>
        <template v-slot:rags="{row}">
            {{ row?.rags ? row.rags.join(",") : "" }}
        </template>
    </ReadWriteView>
    <LabelingTool v-else :id="itemsStore.editing"></LabelingTool>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const router = useRouter()
function goToLabelingConversation(id) {
    itemsStore.editing = id
}

</script>

<style lang="scss" scoped>
.labeling-wrapper {
    margin-left: 146px;
    margin-right: 160px;
    margin-top: 32px;
}
.go-to-view {
    cursor: pointer;
    text-decoration: underline;
    font-weight: 600;
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

