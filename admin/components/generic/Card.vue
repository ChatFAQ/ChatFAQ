<template>
    <el-card class="box-card" @click="itemsStore.editing = item.id">
        <template #header>
            <div class="card-header-title">{{ createTitle(item) }}</div>
        </template>
        <div v-for="(name, prop) in cardProps" class="property">
            <span class="title">{{ name }}:</span>{{ solveRefPropValue(item, prop, itemSchema) }}
        </div>
        <div class="divider">
        </div>
        <div class="commands">
            <el-icon class="command-delete">
                <Delete @click.stop @click="() => {deleting = item.id; deleteDialogVisible = true}"/>
            </el-icon>
            <span class="command-edit" @click="itemsStore.editing = id">{{ $t("edit") }}</span>
        </div>
    </el-card>
    <slot name="extra-card-bottom" :item="item"></slot>
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
import {solveRefPropValue, deleteItem} from "~/utils/index.js";
import {useI18n} from "vue-i18n";

const { t } = useI18n();

const itemsStore = useItemsStore()
const deleting = ref(undefined)
const deleteDialogVisible = ref(false)
const {$axios} = useNuxtApp();

const props = defineProps({
    item: {
        type: Object,
        required: false,
    },
    cardProps: {
        type: Object,
        required: false,
    },
    itemSchema: {
        type: Object,
        required: true,
    },
    titleProps: {
        type: Array,
        required: false,
        default: ["name"],
    },
    apiUrl: {
        type: String,
        required: true,
    },
});


function createTitle(item) {
    return props.titleProps.map(prop => item[prop]).join(" ")
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
.card-header-title {
    font-family: "Montserrat";
    font-size: 18px;
    font-weight: 700;
    line-height: 22px;
    letter-spacing: 0em;
    text-align: left;
    text-overflow: ellipsis;
    overflow-y: hidden;
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
    text-decoration: underline;
    font-weight: 600;
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
</style>
