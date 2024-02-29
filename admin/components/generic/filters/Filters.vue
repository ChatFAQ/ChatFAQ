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
const emit = defineEmits(['change'])

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

watch(() => itemsStore.filters, async () => {  // For when setting filters from outside
    await initForm()
}, {deep: true})

function initForm() {  // For when setting filters from outside
    for (const [filter_name, filter_val] of Object.entries(itemsStore.filters)) {
        if (form.value[filter_name] === undefined)
            form.value[filter_name] = filter_val
    }
}
initForm()

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
    itemsStore.currentPage = 1
    emit("change")
}


</script>
<style lang="scss">
.filters-wrapper {
    .filter-wrapper {
        .filter {
            > div {
                width: 100%;
            }
        }
    }
}
.el-date-editor {
    width: 100% !important;
    min-width: 360px !important;
}
</style>
<style scoped lang="scss">
.filters-wrapper {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
    margin-left: 16px;
    margin-right: 16px;
    margin-top: 26px;
    padding: 16px;
    background-color: white;
    border-radius: 8px;
    border: 1px solid #e0e0e0;

    .filter-wrapper {
        flex: 1;
        margin-right: 16px;

        .filter {
            width: 100%;
            > div {
                width: 100%;
            }
        }
    }
}
</style>
