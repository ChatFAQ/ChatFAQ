<template>
    <div class="demo-pagination-block">
        <el-pagination
            v-model:current-page="itemsStore.currentPage"
            v-model:page-size="itemsStore.pageSize"
            :small="small"
            :disabled="disabled"
            :background="background"
            layout="total, prev, pager, next, jumper"
            :total="itemsStore?.items[props.apiUrl]?.count || 0"
            @current-change="pageChange"
        />
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
</script>

<style scoped>
.demo-pagination-block + .demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}
</style>
