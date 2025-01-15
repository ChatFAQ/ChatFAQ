<template>
    <div class="dashboard-page-title alone">{{ $t('labeling') }}</div>
    <ReadView
        v-if="editing === undefined"
        :readableName="$t('conversation')"
        apiUrl="/back/api/broker/conversations/"
        :tableProps="{
            'fsm_defs': {'name': $t('fsms')},
            'created_date': {'name': $t('created_date'), 'sortable': true},
            'user_id': {'name': $t('userid')},
            'num_user_msgs': {'name': $t('num_user_msgs')},
            'view': {'name': '', 'width': $t('view').length * 20, 'align': 'center'},
        }"
        :defaultSort="{'prop': 'created_date', 'order': 'descending'}"
        :filtersSchema="[
            {'type': 'search', 'placeholder': $t('name'), 'field': 'search'},
            {'type': 'range-date', 'startPlaceholder': $t('startdate'), 'endPlaceholder': $t('enddate'), 'field': 'created_date'},
            {'type': 'ref', 'placeholder': $t('fsm_def'), 'field': 'fsm_def', 'endpoint': '/back/api/fsm/definitions/'},
            {
                'type': 'enum',
                'placeholder': $t('reviewed'),
                'field': 'reviewed',
                'choices': [{'value': 'completed', 'label': $t('completed')}, {'value': 'pending', 'label': $t('pending')}]
            },
            {'type': 'bool', 'field': 'user_feedback_exists', 'placeholder': $t('withuserfeedback')},
        ]"
        :textExplanation="$t('labelingexplanation')"
        read-only
    >
        <template v-slot:view="{row}">
            <div class="go-to-view" @click="goToLabelingConversation(row.id)">{{ $t("view") }}</div>
        </template>
        <template v-slot:fsms="{row}">
            {{ row?.fsms ? row.fsms.join(",") : "" }}
        </template>
    </ReadView>

    <LabelingTool v-else :id="editing" @exit="editing = undefined"></LabelingTool>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import ReadView from "~/components/generic/ReadView.vue";

const itemsStore = useItemsStore()
const editing = ref(undefined)

const router = useRouter()
function goToLabelingConversation(id) {
    editing.value = id
}

</script>

<style lang="scss" scoped>
.go-to-view {
    cursor: pointer;
    text-decoration: underline;
    font-weight: 600;
}
</style>

