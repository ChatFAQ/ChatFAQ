<template>
    <div class="read-view-wrapper">
        <div v-if="items[apiUrl].length" class="section-header">
            <div class="item-count"> {{ $t("numberofitems", {"number": items[apiUrl].length, "readablename": readableName}) }}</div>
            <div class="section-header-right">
                <el-button class="add-button" type="primary" round plain @click="stateToAdd">+
                    {{ $t("additem", {"readablename": readableName}).toUpperCase() }}
                </el-button>
                <div class="selected-icon card-view" :class="{'selected': viewType === 'card'}"
                     @click="viewType = 'card'">
                    <div class="card-icon"></div>
                </div>
                <div class="selected-icon" :class="{'selected': viewType !== 'card'}" @click="viewType = 'table'">
                    <div class="table-icon"></div>
                </div>
            </div>
        </div>
        <div class="cards-view" v-if="viewType === 'card'">
            <el-card v-for="item in items[apiUrl]" class="box-card">
                <template #header>
                    <div class="card-header-title">{{ item[titleProp] }}</div>
                </template>
                <div v-for="(name, prop) in cardProps" class="property">
                    <span class="title">{{ name }}</span>{{ solveRefProp(item, prop) }}
                </div>
                <div class="divider">
                </div>
                <div class="commands">
                    <el-icon class="command-delete">
                        <Delete v-if="deleting !== item.id" @click="deleting = item.id"/>
                        <Check @click="deleteItem(item.id)" v-else/>
                    </el-icon>
                    <span class="command-edit" @click="stateToEdit(item.id)">{{ $t("edit") }}</span>
                </div>
            </el-card>
            <div class="box-card-add" :class="{'no-items': !items[apiUrl].length}" @click="stateToAdd">
                <el-icon>
                    <Plus/>
                </el-icon>
                <span>{{ $t("additem", {"readablename": readableName}) }}</span>
            </div>
        </div>

        <el-table v-else class="table-view" :data="items[apiUrl]" :stripe="false" style="width: 100%">
            <el-table-column v-for="(name, prop) in tableProps" :prop="prop" :label="name" :formatter="(row, column) => solveRefProp(row, column.property)"/>
            <el-table-column align="center">
                <span class="command-edit" @click="stateToEdit(item.id)">{{ $t("edit") }}</span>
            </el-table-column>
            <el-table-column align="center">
                <el-icon class="command-delete">
                    <Delete/>
                </el-icon>
            </el-table-column>
        </el-table>
        <div v-if="viewType !== 'card'" class="table-row-add" :class="{'no-items': !items[apiUrl].length}" @click="stateToAdd">
            <span>
                <el-icon>
                    <Plus/>
                </el-icon>
                {{ $t("additem", {"readablename": readableName}) }}
            </span>
        </div>
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import { storeToRefs } from 'pinia'

const itemsStore = useItemsStore()
const {$axios} = useNuxtApp();
const viewType = ref("card")
const deleting = ref(undefined)
const schema = ref({})


const props = defineProps({
    readableName: {
        type: String,
        required: true,
    },
    apiUrl: {
        type: String,
        required: false,
    },
    cardProps: {
        type: Object,
        required: true,
    },
    tableProps: {
        type: Object,
        required: true,
    },
    titleProp: {
        type: String,
        required: false,
        default: "name",
    },
});

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

function stateToEdit(id) {
    itemsStore.editing = id
}
function stateToAdd() {
    itemsStore.adding = true
}
function deleteItem(id) {
    itemsStore.deleteItem($axios, props.apiUrl, id)
    deleting.value = undefined
}
function solveRefProp(item, propName) {
    const prop = schema.value.properties[propName]
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

.box-card {
    width: 232px;
    margin: 16px;
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

.commands {
    display: flex;
    justify-content: space-between;
    color: $chatfaq-color-primary-500;

    .command-delete {
        margin-left: 16px;
        margin-bottom: 13px;
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
