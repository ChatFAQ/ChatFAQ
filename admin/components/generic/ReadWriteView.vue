<template>
    <client-only>
        <div class="rw-wrapper" v-loading="itemsStore.loading"  element-loading-background="rgba(255, 255, 255, 0.8)">
            <ReadView
                v-if="editing === undefined && !adding"
                @editing="(id) => editing = id"
                @adding="adding = true"
                :apiUrl="apiUrl"
                :readableName="readableName"
                :cardProps="cardProps"
                :tableProps="tableProps"
                :titleProps="titleProps"
                :readOnly="readOnly"
                :defaultSort="defaultSort"
                :defaultFilters="defaultFilters"
                :filtersSchema="filtersSchema"
                :requiredFilter="requiredFilter"
                :textExplanation="textExplanation"
                ref="readView"
            >
                <template v-for="(_, name) in $slots" v-slot:[name]="data">
                    <slot :name="name" v-bind="data"></slot>
                </template>
            </ReadView>
            <WriteView
                v-else
                @exit="toReadView"
                :readableName="readableName"
                :apiUrl="apiUrl"
                :itemId="editing"
                :titleProps="titleProps"
                :excludeFields="excludeFields"
                :conditionalIncludedFields="conditionalIncludedFields"
                :sections="sections"
                :outsideSection="outsideSection"
                v-bind="$attrs"
                :readOnly="readOnly"
                :order="order"
                :backButton="backButton"
                :commandButtons="commandButtons"
                :leaveAfterSave="leaveAfterSave"
            >
                <template v-for="(_, name) in $slots" v-slot:[name]="data">
                    <slot :name="name" v-bind="data"></slot>
                </template>
            </WriteView>
        </div>
    </client-only>
</template>

<script setup>
import ReadView from "~/components/generic/ReadView.vue";
import {defineProps} from 'vue';
import WriteView from "~/components/generic/WriteView.vue";
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()
const readView = ref(undefined)
const editing = ref(undefined)
const adding = ref(false)
defineExpose({readView, toReadView, editing})

const props = defineProps({
    readableName: {
        type: String,
        mandatory: true
    },
    apiUrl: {
        type: String,
        mandatory: true
    },
    cardProps: {
        type: Object,
        mandatory: true
    },
    tableProps: {
        type: Object,
        mandatory: true
    },
    titleProps: {
        type: Array,
        required: false,
        default: ["name"],
    },
    excludeFields: {
        type: Array,
        required: false,
        default: [],
    },
    conditionalIncludedFields: { // the values are the only fields that are conditionally included if the keys (fields names) are present in the form
        type: Object,
        required: false,
        default: undefined,
    },
    sections: {
        type: Object,
        required: false,
        default: {},
    },
    defaultSort: {
        type: Object,
        required: false,
        default: {},
    },
    defaultFilters: {
        type: Object,
        required: false,
        default: undefined,
    },
    outsideSection: {
        type: Array,
        required: false,
        default: [],
    },
    readOnly: {
        type: Boolean,
        required: false,
        default: false,
    },
    filtersSchema: {
        type: Array,
        required: false,
    },
    requiredFilter: {
        type: String,
        required: false,
    },
    textExplanation: {
        type: String,
        required: false,
    },
    order: {
        type: Array,
        required: false,
        default: undefined,
    },
    backButton: {
        type: Boolean,
        required: false,
        default: true,
    },
    commandButtons: {
        type: Boolean,
        required: false,
        default: true,
    },
    leaveAfterSave: {
        type: Boolean,
        required: false,
        default: true,
    },
    itemId: {
        type: [String, Number],
        required: false,
        default: undefined,
    },
})
if (props.itemId)
    editing.value = props.itemId
watch(() => props.itemId, (newVal) => {
    editing.value = newVal
})

function toReadView() {
    adding.value = false
    editing.value = undefined
}

</script>
<style lang="scss">
.el-loading-mask {
    background-color: unset;
}
</style>

<style scoped lang="scss">
.rw-wrapper {
    min-height: calc(100vh - 300px);
}

</style>
