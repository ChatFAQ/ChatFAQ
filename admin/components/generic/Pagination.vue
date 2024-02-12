<template>
    <div class="pagination-wrapper">
        <div class="total"> Total: {{total}}
        </div>
        <el-pagination
            v-if="total > itemsStore.pageSize"
            v-model:current-page="itemsStore.currentPage"
            v-model:page-size="itemsStore.pageSize"
            :small="small"
            :disabled="disabled"
            :background="background"
            layout="prev, pager, next"
            :total="itemsStore?.items[props.apiUrl]?.count || 0"
            @current-change="pageChange"
        />
        <div></div>
    </div>

</template>
<script lang="ts" setup>
import {useItemsStore} from "~/store/items.js";
import {ref} from 'vue'
const {$axios} = useNuxtApp();

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
});

const itemsStore = useItemsStore()
const small = ref(false)
const background = ref(false)
const disabled = ref(false)
const pageChange = async (val: number) => {
    itemsStore.loading = true
    itemsStore.currentPage = val
    await itemsStore.retrieveItems($axios, props.apiUrl)
    itemsStore.loading = false
}
const total = computed(() => {
    return itemsStore?.items[props.apiUrl]?.count || 0
})

</script>
<style lang="scss">

.el-pagination {
    li.number, .btn-next, .btn-prev, .btn-quicknext, .btn-quickprev {
        background-color: transparent !important;
        border-radius: 2px !important;
        border: 1px solid $chatfaq-color-primary-200 !important;
        width: 32px !important;
        height: 32px !important;
        margin-right: 8px !important;
        color: $chatfaq-color-greyscale-800 !important;
        &[disabled] {
            color: $chatfaq-color-primary-200 !important;
            border-color: $chatfaq-color-primary-200 !important;
        }
        &.is-active {
            border-color: $chatfaq-color-primary-500 !important;
            color: $chatfaq-color-primary-500 !important;
        }

    }
}

</style>

<style scoped lang="scss">
.pagination-wrapper {
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
    margin: 8px 16px 16px;

    .total {
        color: $chatfaq-color-greyscale-800;
        font-size: 14px;
        font-weight: 400;
    }
}
</style>
