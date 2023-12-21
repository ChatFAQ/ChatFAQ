<template>
    <div class="dashboard-page-title">{{ $t('labeling') }}</div>
    <ReadWriteView
        :readableName="$t('conversation')"
        apiUrl="/back/api/broker/conversations/"
        :tableProps="{
                    'name': $t('name'),
                }"
        read-only
    >
        <template v-slot:data="props">
            <FieldData :form="props.form" :fieldName="props.fieldName" ref="fieldData">123</FieldData>
        </template>
    </ReadWriteView>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";
import FieldData from "~/components/widget_config/fields/FieldData.vue";

const fieldData = ref(null)

const {$axios} = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("widgetsettings")
await itemsStore.loadSchema($axios)

function submitFieldData() {
    fieldData.value.submit()
}
</script>
