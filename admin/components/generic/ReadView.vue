<template>
    <div class="read-view-wrapper" v-loading="itemsStore.loading" element-loading-background="rgba(255, 255, 255, 0.8)">
        <div v-if="textExplanation" class="text-explanation" v-html="textExplanation"></div>
        <Filters v-if="filtersSchema" :filtersSchema="filtersSchema"/>
        <div class="section-header">
            <slot name="legend" :total="itemsStore.items[apiUrl]?.results?.length">
                <div class="item-count"> {{
                        $t("numberofitems", {
                            "number": itemsStore.items[apiUrl]?.results.length,
                            "readablename": readableName
                        })
                    }}
                </div>
            </slot>
            <div class="section-header-right">
                <el-button v-if="!readOnly" class="add-button" :class="{'not-only-command': cardProps && tableProps}"
                           type="primary" round plain @click="stateToAdd">+
                    {{ $t("additem", {"readablename": readableName}).toUpperCase() }}
                </el-button>
                <div v-if="cardProps && tableProps" class="selected-icon card-view"
                     :class="{'selected': !itemsStore.tableMode }"
                     @click="itemsStore.tableMode = false">
                    <div class="card-icon"></div>
                </div>
                <div v-if="cardProps && tableProps" class="selected-icon" :class="{'selected': itemsStore.tableMode }"
                     @click="itemsStore.tableMode = true">
                    <div class="table-icon"></div>
                </div>
            </div>
        </div>
        <div class="cards-view" v-if="!itemsStore.tableMode && cardProps && requiredFilterSatisfied">
            <Card v-for="item in itemsStore.items[apiUrl]?.results" :item="item" :cardProps="cardProps" :titleProps="titleProps" :apiUrl="apiUrl" :itemSchema="itemSchema">
                <template v-slot:extra-card-bottom="{item}">
                    <slot name="extra-card-bottom" :item="item"></slot>
                </template>
            </Card>
            <div class="box-card-add" :class="{'no-items': !itemsStore.items[apiUrl]?.results.length}"
                 @click="stateToAdd">
                <div class="box-card-add-content">
                    <el-icon>
                        <Plus/>
                    </el-icon>
                    <span>{{ $t("additem", {"readablename": readableName}) }}</span>
                </div>
            </div>
        </div>
        <el-table v-else-if="requiredFilterSatisfied"
                  class="table-view"
                  :data="itemsStore.items[apiUrl]?.results"
                  :stripe="false"
                  :defaultSort="defaultSort"
                  sortable="custom"
                  @sort-change="sortChange"
                  style="width: 100%">
            <el-table-column
                v-for="(propInfo, prop) in tableProps"
                :prop="prop"
                :label="propInfo.name"
                :formatter="(row, column) => propInfo.formatter ? propInfo.formatter(row, column.property) : solveRefPropValue(row, column.property, itemSchema)"
                :width="propInfo.width ? propInfo.width : undefined"
                :align="propInfo.align ? propInfo.align : undefined"
                :sortable="propInfo.sortable"
                :sortMethod="propInfo.sortMethod"
            >
                <template v-if="$slots[prop]" #default="scope">
                    <slot :name="prop" v-bind="scope"></slot>
                </template>
            </el-table-column>
            <el-table-column v-if="!readOnly" align="center" :width="$t('edit').length * 13">
                <template #default="{ row }">
                    <span class="command-edit" @click="itemsStore.editing = row.id">{{ $t("edit") }}</span>
                </template>
            </el-table-column>
            <el-table-column v-if="!readOnly" align="center" width="100">
                <template #default="{ row }">
                    <el-icon class="command-delete">
                        <Delete @click="() => {deleting = row.id; deleteDialogVisible = true}"/>
                    </el-icon>
                </template>
            </el-table-column>
        </el-table>
        <div v-if="itemsStore.tableMode && !readOnly" class="table-row-add"
             :class="{'no-items': !itemsStore.items[apiUrl]?.results.length}"
             @click="stateToAdd">
            <span>
                <el-icon>
                    <Plus/>
                </el-icon>
                {{ $t("additem", {"readablename": readableName}) }}
            </span>
        </div>
        <Pagination :apiUrl="props.apiUrl"/>
    </div>
    <el-dialog v-model="deleteDialogVisible" :title="$t('warning')" width="500" center>
        <span>
            {{ $t('deleteitemwarning') }}
        </span>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="() => {deleting = undefined; deleteDialogVisible = false}">{{ $t('cancel') }}</el-button>
                <el-button type="primary" @click="delItem">
                    {{ $t('confirm') }}
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import Pagination from "~/components/generic/Pagination.vue";
import {useRoute} from 'vue-router'
import Filters from "~/components/generic/filters/Filters.vue";
import Card from "~/components/generic/Card.vue";
import {useI18n} from "vue-i18n";
import {solveRefPropValue, deleteItem} from "~/utils/index.js";
import {storeToRefs} from 'pinia'

const { t } = useI18n();
const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const deleting = ref(undefined)
const deleteDialogVisible = ref(false)
const {schema} = storeToRefs(itemsStore)
const itemSchema = ref({})
const route = useRoute()

const props = defineProps({
    readableName: {
        type: String,
        required: true,
    },
    apiUrl: {
        type: String,
        required: true,
    },
    cardProps: {
        type: Object,
        required: false,
    },
    tableProps: {
        type: Object,
        required: true,
    },
    defaultSort: {
        type: Object,
        required: false,
        default: {},
    },
    titleProps: {
        type: Array,
        required: false,
        default: ["name"],
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
    }
});

const requiredFilterSatisfied = computed(() => {
    return !props.requiredFilter || itemsStore.filters[props.requiredFilter] !== undefined
})

function initStoreWatchers() {
    watch(() => route.fullPath, () => {
        itemsStore.currentPage = 1
    })

    watch(() => itemsStore.filters, async () => {
        await loadItems()
    }, {deep: true})

    watch(() => itemsStore.currentPage, async () => {
        await loadItems()
    })

    watch(() => itemsStore.ordering, async () => {
        await loadItems()
    })
}

async function initData() {
    itemsStore.loading = true
    itemSchema.value = await itemsStore.getSchemaDef($axios, props.apiUrl)
    sortChange(props.defaultSort)
    await loadItems()
    initStoreWatchers()
}

async function loadItems() {
    itemsStore.loading = true
    if (!requiredFilterSatisfied.value) {
        itemsStore.loading = false
        itemsStore.items[props.apiUrl] = {results: []}
        return
    }
    await itemsStore.retrieveItems($axios, props.apiUrl)
    itemsStore.loading = false
}

await initData()

function stateToAdd() {
    itemsStore.adding = true
}

function sortChange({column, prop, order}) {
    if (!order)
        itemsStore.ordering = undefined
    else if (order === "descending")
        itemsStore.ordering = `-${prop}`
    else
        itemsStore.ordering = prop
}


async function delItem() {
    await deleteItem(deleting.value, itemsStore, props.apiUrl, t, $axios);
    deleting.value = undefined;
    deleteDialogVisible.value = false
}
</script>

<style lang="scss">


.el-dialog {
    border-radius: 10px;
    .el-dialog__header {
        text-align: left;
        .el-dialog__title {
            color: $chatfaq-color-primary-500 !important;
            font-size: 16px;
            font-weight: 600;
        }
    }
    .el-dialog__body {
        text-align: left;
        color: $chatfaq-color-neutral-black !important;
        font-size: 14px;
        font-weight: 400;
    }
}

.el-card {
    border-radius: 10px;
    border: 1px solid $chatfaq-color-primary-200;
    box-shadow: unset !important;
}

.el-card__header {
    padding-left: 16px;
    border: unset;
    display: flex;
    justify-content: space-between;
}

.el-card__body {
    padding: unset;
}

.el-icon {
    height: unset;
}

.el-table__header-wrapper {
    th {
        background-color: $chatfaq-color-primary-200 !important;
    }
}

.el-table {
    border-radius: 10px;

    * {
        color: $chatfaq-color-primary-500;
    }

    tbody > tr:nth-child(even) {
        // background: #DFDAEA66;
    }
}

.el-card:hover {
}
</style>

<style lang="scss" scoped>
.read-view-wrapper {
    display: flex;
    flex-wrap: wrap;
    margin-left: 160px;
    margin-right: 160px;
    max-width: 1300px;
}

.cards-view {
    display: grid;
    flex-wrap: wrap;
    width: 100%;
    justify-items: stretch;
    grid-template-columns: repeat(auto-fill, minmax(100px, 25%));
}

/* Override justify-content for the last row */
.cards-view::after {
    content: "";
    flex: auto;
}

.table-view {
    margin: 16px;
}

.box-card-add {
    width: 100%;
    padding: 16px;
    color: $chatfaq-color-primary-500;
    box-sizing: border-box;
    cursor: pointer;

    .box-card-add-content {
        border: 1px dashed $chatfaq-color-primary-500;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        width: 100%;
        height: 100%;
        padding-top: 30px;
        padding-bottom: 30px;

        &:hover {
            background: linear-gradient(0deg, rgba(223, 218, 234, 0.4), rgba(223, 218, 234, 0.4));
        }

        &.no-items {
            width: 100%;
            padding: 24px;
            margin-top: 25px;
        }

        i {
            width: 100%;
            margin-bottom: 17px;
        }
    }
}

.table-row-add {
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    width: 100%;
    padding: 10px;
    margin: 16px;
    color: $chatfaq-color-primary-500;
    border: 1px dashed $chatfaq-color-primary-500;
    border-radius: 10px;
    cursor: pointer;

    span {
        display: flex;
        justify-content: center;

        i {
            margin-right: 10px;
        }
    }
}

.text-explanation {
    margin-right: 16px;
    margin-left: 16px;
    margin-top: 26px;
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    padding-left: 18px;
    border-left: 2px solid $chatfaq-color-primary-500;

}

.section-header {
    display: flex;
    width: 100%;
    justify-content: space-between;
    margin-right: 16px;
    margin-left: 16px;
    margin-top: 26px;

    .item-count {
        display: flex;
        justify-content: center;
        flex-direction: column;
        font-size: 12px;
        font-weight: 400;
        line-height: 16px;
        letter-spacing: 0px;
        text-align: left;
        color: $chatfaq-color-greyscale-800;

    }

    .section-header-right {
        display: flex;
        .add-button {
            @include button-round;
        }
        > .add-button.not-only-command {
            margin-right: 32px;
        }

        > .selected-icon.card-view {
            margin-right: 8px;
        }
    }

}

.selected-icon {
    width: 32px;
    height: 32px;
    text-align: center;
    position: relative;
    border-radius: 4px;
    margin: auto;

    &:hover {
        cursor: pointer;
    }

    &.selected {
        background-color: $chatfaq-color-primary-200;
    }

    > div {
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
        width: 16px;
        height: 16px;
        margin: auto;
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
    }

    > .card-icon {
        background-image: url('~/assets/icons/card-view-icon.svg');
    }

    > .table-icon {
        background-image: url('~/assets/icons/table-view-icon.svg');
    }
}
</style>
