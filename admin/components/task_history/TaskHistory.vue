<template>
    <div class="dashboard-page-title alone">{{ $t('tasks') }}</div>
    <ReadWriteView
        apiUrl="/back/api/language-model/tasks/"
        :readOnly="true"
        :readable-name='$t("asynctasks")'
        :tableProps="{
            'status': {'name': '', 'width': 50},
            'task_name': {'name': $t('task_name')},
            'date_created': {'name': $t('date_created'), 'sortable': true, 'sortMethod': sortDates},
            'duration': {'name': $t('duration'), 'sortable': true, 'sortMethod': sortDuration},
            'view': {'name': $t('view')},
        }"
        :sections="{
            [$t('generalinfo')]: [
                'status',
                'task_name',
                'periodic_task_name',
                'task_args',
                'task_kwargs',
                'worker',
                'content_type',
                'content_encoding',
                'result',
                'date_created',
                'date_done',
                'meta',
            ],
            [$t('logs')]: [
                'traceback',
            ]
        }"
    >
        <template #legend>
            <div class="legend"><span>Status:</span>
                <span><span class="status success"></span>{{ $t("success") }}</span>
                <span><span class="status started"></span>{{ $t("started") }}</span>
                <span><span class="status waiting"></span>{{ $t("waiting") }}</span>
                <span><span class="status failure"></span>{{ $t("failure") }}</span>
            </div>
        </template>
        <template v-slot:duration="{row}">
            <div>{{ calculateDuration(row) }}</div>
        </template>
        <template v-slot:date_created="{row}">
            <div>{{ formatDate(row.date_created) }}</div>
        </template>
        <template v-slot:task_name="{row}">
            <div>{{ formatTaskName(row.task_name) }}</div>
        </template>
        <template v-slot:status="{row}">
            <div width="10" class="status" :class="{[row.status.toLowerCase()]: true}">-</div>
        </template>
        <template v-slot:view="{row}">
            <span class="command-edit" @click="stateToDetail(row.id)">{{ $t("view") }}</span>
        </template>
        <template v-slot:write-traceback="value">
            <div class="traceback">{{ value["value"] }}</div>
        </template>
    </ReadWriteView>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";

const password = ref(null)

const {$axios} = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("tasks")
await itemsStore.loadSchema($axios)


function calculateDuration({date_created, date_done}) {
    // Calculate duration in mili, secs, minutes or hours depending on the diration itself, format of imput dates are: 2023-12-11T16:08:44.661922
    if (date_done) {
        const dateCreated = new Date(date_created)
        const dateFinished = new Date(date_done)
        let diff = dateFinished - dateCreated
        if (diff < 1000) {
            return `${diff.toFixed(1)} ms`
        } else if (diff < 60000) {
            return `${(diff / 1000).toFixed(1)} s`
        } else if (diff < 3600000) {
            return `${(diff / 60000).toFixed(1)} min`
        } else {
            return `${(diff / 3600000).toFixed(1)} h`
        }
    } else {
        return null
    }
}

function formatDate(date) {
    if (date) {
        const dateObj = new Date(date)
        return `${dateObj.getDate()}/${dateObj.getMonth() + 1}/${dateObj.getFullYear()} ${dateObj.getHours()}:${dateObj.getMinutes()}:${dateObj.getSeconds()}`
    } else {
        return null
    }
}

function formatTaskName(name) {
    if (!name) {
        return null
    }
    return name.split(".")[name.split(".").length - 1]
}

function stateToDetail(id) {
    itemsStore.editing = id
}

function sortDates(a, b) {
    const dateA = new Date(a.date_created)
    const dateB = new Date(b.date_created)
    return dateA - dateB
}
function sortDuration(a, b) {
    a = calculateDuration(a)
    b = calculateDuration(b)
    // check if any is null:
    if (!a) {
        return 1
    } else if (!b) {
        return -1
    }
    // a and b are strings with the next format: 1.2 s, 1.2 min, 1.2 h, etc...
    const aNumber = parseFloat(a.split(" ")[0])
    const bNumber = parseFloat(b.split(" ")[0])
    const aUnit = a.split(" ")[1]
    const bUnit = b.split(" ")[1]
    if (aUnit === bUnit) {
        return aNumber - bNumber
    } else if (aUnit === "ms") {
        return -1
    } else if (aUnit === "s" && bUnit === "min") {
        return -1
    } else if (aUnit === "s" && bUnit === "h") {
        return -1
    } else if (aUnit === "min" && bUnit === "h") {
        return -1
    } else {
        return 1
    }
}
</script>
<style lang="scss" scoped>
.status {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin: 0 auto;
    background-color: #F2C94C; // waiting

    &.success {
        background-color: #27AE60;
    }

    &.failure {
        background-color: #EB5757;
    }

    &.started {
        background-color: #2D9CDB;
    }
}

.legend {
    font-size: 12px;
    font-weight: 400;
    line-height: 18px;
    letter-spacing: 0px;
    text-align: left;
    color: $chatfaq-color-greyscale-800;
    .status {
        display: inline-block;
    }
    > span {
        margin-right: 32px;
        > span {
            margin-right: 6px;
        }
    }

}

.command-edit {
    cursor: pointer;
    text-decoration: underline;
}
.traceback {
    white-space: pre-wrap;
}
</style>
