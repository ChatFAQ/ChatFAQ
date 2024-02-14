<template>
    <Filters v-if="filtersSchema" :apiUrl="apiUrl" :filtersSchema="filtersSchema"/>
    <div class="read-view-wrapper" v-loading="itemsStore.loading" element-loading-background="rgba(255, 255, 255, 0.8)">
        <div v-if="items[apiUrl]?.results.length" class="section-header">
            <slot name="legend" :total="items[apiUrl]?.results.length">
                <div class="item-count"> {{
                        $t("numberofitems", {
                            "number": items[apiUrl]?.results.length,
                            "readablename": readableName
                        })
                    }}
                </div>
            </slot>
            <div class="section-header-right">
                <el-button v-if="!readOnly" class="add-button" type="primary" round plain @click="stateToAdd">+
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
        <div class="cards-view" v-if="!itemsStore.tableMode && cardProps">
            <div v-for="item in items[apiUrl]?.results" class="card-wrapper">
                <el-card class="box-card" @click="stateToEdit(item.id)">
                    <template #header>
                        <div class="card-header-title">{{ createTitle(item) }}</div>
                    </template>
                    <div v-for="(name, prop) in cardProps" class="property">
                        <span class="title">{{ name }}</span>
                    </div>
                    <div class="divider">
                    </div>
                    <div class="commands">
                        <el-icon v-if="deleting !== item.id" class="command-delete">
                            <Delete @click="deleting = item.id"/>
                        </el-icon>
                        <div class="command-delete-confirm">
                            <el-icon v-if="deleting === item.id" class="command-delete">
                                <Close @click="deleting = undefined"/>
                            </el-icon>
                            <el-icon v-if="deleting === item.id" class="command-delete">
                                <Check @click="deleteItem(deleting)"/>
                            </el-icon>
                        </div>
                        <!-- <span class="command-edit" @click="stateToEdit(item.id)">{{ $t("edit") }}</span> -->
                    </div>
                </el-card>
                <slot name="extra-card-bottom" :item="item"></slot>
            </div>
            <div class="box-card-add" :class="{'no-items': !items[apiUrl]?.results.length}" @click="stateToAdd">
                <el-icon>
                    <Plus/>
                </el-icon>
                <span>{{ $t("additem", {"readablename": readableName}) }}</span>
            </div>
        </div>

        <el-table v-else class="table-view" :data="items[apiUrl]?.results" :stripe="false" :defaultSort="defaultSort"
                  style="width: 100%">
            <el-table-column
                v-for="(propInfo, prop) in tableProps"
                :prop="prop"
                :label="propInfo.name"
                :formatter="(row, column) => propInfo.formatter ? propInfo.formatter(row, column.property) : solveRefProp(row, column.property)"
                :width="propInfo.width ? propInfo.width : undefined"
                :sortable="propInfo.sortable"
                :sortMethod="propInfo.sortMethod"
            >
                <template v-if="$slots[prop]" #default="scope">
                    <slot :name="prop" v-bind="scope"></slot>
                </template>
            </el-table-column>
            <el-table-column v-if="!readOnly" align="center">
                <template #default="{ row }">
                    <span class="command-edit" @click="stateToEdit(row.id)">{{ $t("edit") }}</span>
                </template>
            </el-table-column>
            <el-table-column v-if="!readOnly" align="center">
                <template #default="{ row }">
                    <el-icon v-if="deleting !== row.id" class="command-delete">
                        <Delete @click="deleting = row.id"/>
                    </el-icon>
                    <div class="command-delete-confirm on-table">
                        <el-icon v-if="deleting === row.id" class="command-delete">
                            <Close @click="deleting = undefined"/>
                        </el-icon>
                        <el-icon v-if="deleting === row.id" class="command-delete">
                            <Check @click="deleteItem(deleting)"/>
                        </el-icon>
                    </div>
                </template>
            </el-table-column>
        </el-table>
        <div v-if="itemsStore.tableMode && !readOnly" class="table-row-add"
             :class="{'no-items': !items[apiUrl]?.results.length}"
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
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import {storeToRefs} from 'pinia'
import Pagination from "~/components/generic/Pagination.vue";
import { useRoute } from 'vue-router'
import Filters from "~/components/generic/filters/Filters.vue";

const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const deleting = ref(undefined)
const schema = ref({})
const route = useRoute()

watch(() => route.fullPath, () => {
    itemsStore.currentPage = 1
})

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
        required: true,
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
    }
});

itemsStore.loading = true
const {data} = await useAsyncData(
    "schema_" + props.apiUrl,
    async () => await itemsStore.getSchemaDef($axios, props.apiUrl)
)
schema.value = data.value

await useAsyncData(
    props.apiUrl,
    async () => await itemsStore.retrieveItems($axios, props.apiUrl)
)

const {items} = storeToRefs(itemsStore)
itemsStore.loading = false

function createTitle(item) {
    return props.titleProps.map(prop => item[prop]).join(" ")
}

function stateToEdit(id) {
    itemsStore.editing = id
}

function stateToAdd() {
    itemsStore.adding = true
}

function deleteItem(id) {
    itemsStore.loading = true
    itemsStore.deleteItem($axios, props.apiUrl, id)
    deleting.value = undefined
    itemsStore.loading = false
}

function solveRefProp(item, propName) {
    const prop = schema.value.properties[propName]
    if (!prop)
        return item[propName]
    if (prop.$ref && schema.value.properties[propName].choices) {
        // schema.choices has the values for the $ref: [{label: "label", value: "value"}, {...}] item[propName] has the value, we want the label
        const choice = schema.value.properties[propName].choices.find(choice => choice.value === item[propName])
        if (choice) {
            return choice.label
        }
    }
    return item[propName]

}
</script>

<style lang="scss">
.el-card {
    border-radius: 10px;
    border: 1px solid $chatfaq-color-primary-200;
    box-shadow: unset !important;
}

.el-card__header {
    padding-left: 16px;
    border: unset;
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
    margin-left: 120px;
    margin-right: 120px;
    max-width: 1300px;
}

.cards-view {
    display: flex;
    justify-content: auto;
    flex-wrap: wrap;
    width: 100%;
}

/* Override justify-content for the last row */
.cards-view::after {
    content: "";
    flex: auto;
}

.table-view {
    margin: 16px;
}

.card-wrapper {
    width: 232px;
    margin: 16px;

    .box-card {
        cursor: pointer;

        &:hover {
            box-shadow: 0px 4px 4px 0px #DFDAEA66 !important;
        }
    }
}

.box-card-add {
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    padding: 18px;
    width: 232px;
    margin: 16px;
    color: $chatfaq-color-primary-500;
    border: 1px dashed $chatfaq-color-primary-500;
    border-radius: 10px;
    cursor: pointer;

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

.card-header-title {
    font-size: 18px;
    font-weight: 700;
    line-height: 22px;
    letter-spacing: 0em;
    text-align: left;
}

.property {
    overflow: hidden;
    width: 100%;
    text-overflow: ellipsis;
    display: inline-block;
    white-space: nowrap;
    padding-left: 16px;

    .title {
        font-size: 14px;
        font-weight: 600;
        line-height: 20px;
        letter-spacing: 0em;
        text-align: left;
        color: $chatfaq-color-primary-500;
        margin-right: 10px;

    }
}

.divider {
    width: 100%;
    height: 1px;
    background-color: $chatfaq-color-primary-200;
    margin-top: 10px;
    margin-bottom: 13px;
}

.command-edit, .command-delete {
    cursor: pointer;
}

.command-delete-confirm.on-table {
    .command-delete {
        margin-right: 10px;
    }
}

.commands {
    display: flex;
    justify-content: space-between;
    color: $chatfaq-color-primary-500;

    .command-delete {
        margin-left: 16px;
        margin-bottom: 13px;
    }

    .command-delete-confirm {
        display: flex;
        justify-content: center;
    }

    .command-edit {
        margin-right: 16px;
        margin-bottom: 13px;
    }
}

.section-header {
    display: flex;
    width: 100%;
    justify-content: space-between;
    margin-right: 16px;
    margin-left: 16px;
    margin-top: 9px;

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

        > .add-button {
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
