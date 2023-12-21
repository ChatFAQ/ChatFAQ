<template>
    <div class="dashboard-page-title">{{ $t('labeling') }}</div>
    <ReadWriteView
        v-if="itemsStore.editing === undefined"
        :readableName="$t('conversation')"
        apiUrl="/back/api/broker/conversations/"
        :tableProps="{
                    'name': {'name': $t('name')},
                    'created_date': {'name': $t('created_date')},
                    'view': {'name': $t('view')},
                }"
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

