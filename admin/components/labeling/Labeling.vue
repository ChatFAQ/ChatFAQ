<template>
    <div class="dashboard-page-title alone">{{ $t('labeling') }}</div>
    <ReadWriteView
        v-if="itemsStore.editing === undefined"
        :readableName="$t('conversation')"
        apiUrl="/back/api/broker/conversations/"
        :tableProps="{
            'name': {'name': $t('name')},
            'created_date': {'name': $t('created_date'), 'sortable': true},
            'user_id': {'name': $t('userid')},
            'view': {'name': ''},
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
            <div class="go-to-view" @click="goToLabelingConversation(row.id)">{{ $t("View") }}</div>
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
.go-to-view {
    cursor: pointer;
    text-decoration: underline;
}
</style>

