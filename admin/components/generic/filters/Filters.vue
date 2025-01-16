<template>
    <div class="filters-wrapper">
        <div class="filter-wrapper" v-for="filterInfo in filtersSchema">
            <div class="filter" v-if="filterInfo.type === 'search'">
                <el-input v-model="form[filterInfo.field]"
                          @input="submitFiltersDebounce"
                          :placeholder="filterInfo.placeholder"
                          suffix-icon="Search"
                          clearable
                ></el-input>
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
            <div class="filter" v-else-if="filterInfo.type === 'bool'">
                <el-checkbox v-model="form[filterInfo.field]"
                          @input="submitFiltersDebounce" :label="filterInfo.placeholder"
                ></el-checkbox>
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import {useItemsStore} from "~/store/items.js";
import InputSelect from "~/components/generic/InputSelect.vue";
const itemsStore = useItemsStore()
const filters = ref({})

const ignoreParams = ['offset', 'limit', 'id'];
const emit = defineEmits(["change"])

const props = defineProps({
    filtersSchema: {
        type: Array,
        required: false,
    },
    initialFiltersValues: {
        type: Object,
        required: false,
        default: {},
    },
});
const form = ref(props.initialFiltersValues)

if (Object.keys(form.value).length > 0) {
    submitFilters()
}
watch(() => props.initialFiltersValues, (newValue) => {
    form.value = newValue
    submitFilters()
}, {deep: true})

defineExpose({filters, form})

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
    const _filters = {}
    for (const [key, value] of Object.entries(form.value)) {
        if (key.indexOf("__gte") !== -1 || key.indexOf("__lte") !== -1)
            continue
        if (Array.isArray(value)) {
            if (value.length > 0) {
                _filters[key + "__gte"] = value[0].toISOString().split('T')[0]
                _filters[key + "__lte"] = value[1].toISOString().split('T')[0]
            }
        } else if (value !== undefined && value !== false && !ignoreParams.includes(key)) {
            _filters[key] = value
        }
    }
    itemsStore.currentPage = 1
    filters.value = _filters
    emit("change", filters.value)
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
