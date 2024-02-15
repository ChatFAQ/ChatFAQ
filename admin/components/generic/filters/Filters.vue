<template>
    <div class="filters-wrapper">
        <div class="filter-wrapper" v-for="filterInfo in filtersSchema">
            <div class="filter" v-if="filterInfo.type === 'search'">
                <el-input v-model="form[filterInfo.field]" @input="submitFiltersDebounce" :placeholder="filterInfo.placeholder"
                          clearable></el-input>
            </div>
            <div class="filter" v-else-if="filterInfo.type === 'range-date'">
                <el-date-picker
                    type="datetimerange"
                    v-model="form[filterInfo.field]"
                    @change="submitFilters"
                    :range-separator="$t('to')"
                    :start-placeholder="filterInfo.startPlaceholder"
                    :end-placeholder="filterInfo.endPlaceholder"
                />
            </div>
            <div class="filter" v-else-if="filterInfo.type === 'ref' || filterInfo.type === 'enum'">
                <InputSelect :filterSchema="filterInfo"
                             :form="form"
                             :fieldName="filterInfo.field"
                             :placeholder="filterInfo.placeholder"
                             @change="submitFilters"
                />
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import {useItemsStore} from "~/store/items.js";
import InputSelect from "~/components/generic/InputSelect.vue";

const {$axios} = useNuxtApp();
const itemsStore = useItemsStore()
const form = ref({})

const ignoreParams = ['offset', 'limit', 'id'];

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    filtersSchema: {
        type: Array,
        required: false,
    },
});
for (const fieldInfo of props.filtersSchema) {
    form[fieldInfo.field] = undefined
}

function debounce(func, timeout = 500) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(async () => {
            await func.apply(this, args);
        }, timeout);
    };
}

const submitFiltersDebounce = debounce(async () => await submitFilters());

async function submitFilters() {
    itemsStore.loading = true
    const fitlers = {}
    for (const [key, value] of Object.entries(form.value)) {
        if (Array.isArray(value)) {
            if (value.length > 0) {
                fitlers[key + "__gte"] = value[0].toISOString().split('T')[0]
                fitlers[key + "__lte"] = value[1].toISOString().split('T')[0]
            }
        } else if (value !== undefined && !ignoreParams.includes(key)) {
            fitlers[key] = value
        }
    }
    itemsStore.filters = fitlers
    await itemsStore.retrieveItems($axios, props.apiUrl)
    itemsStore.loading = false
}


</script>
<style scoped lang="scss">
.filters-wrapper {
    display: flex;
    flex-wrap: wrap;
    margin-left: 136px;
    margin-right: 136px;
    max-width: 1300px;
    width: fit-content;
    padding: 16px;
    background-color: white;
    border-radius: 8px;
    border: 1px solid #e0e0e0;

    .filter {
        margin-right: 16px;
    }
}
</style>