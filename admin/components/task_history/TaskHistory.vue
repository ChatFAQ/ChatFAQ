<template>
    <div class="dashboard-page-title alone">{{ $t('tasks') }}</div>
    <ReadWriteView
        apiUrl="/back/api/language-model/tasks/"
        :readOnly="true"
        :readable-name='$t("asynctasks")'
        :tableProps="{
            'state': {'name': '', 'width': 50},
            'name': {'name': $t('task_name')},
            'creation_time_ms': {'name': $t('date_created'), 'sortable': true, 'sortMethod': sortDates, 'formatter': timeMSFormatter},
            'duration': {'name': $t('duration'), 'sortable': false, 'sortMethod': sortDuration, 'formatter': durationMSFormatter},
            'view': {'name': '', 'width': $t('view').length * 20, 'align': 'center'},
        }"
        itemIdProp="task_id"
        :sections="{
            [$t('logs')]: [
                'logs_link',
            ],
            [$t('generalinfo')]: [
                'name',
                'state',
                'creation_time_ms',
                'start_time_ms',
                'end_time_ms',
                'error_type',
                'task_id',
                'job_id',
                'attempt_number',
                'actor_id',
                'type',
                'func_or_class_name',
                'parent_task_id',
                'node_id',
                'worker_id',
                'worker_pid',
                'language',
                'required_resources',
                'placement_group_id',
                'runtime_env_info',
                'events',
                'profiling_data',
            ]
        }"
        :itemId="itemsStore.taskID"
    >
        <template #legend>
            <div class="legend"><span>Status:</span>
                <span><span class="status FINISHED"></span>{{ $t("success") }}</span>
                <span><span class="status RUNNING"></span>{{ $t("started") }}</span>
                <span><span class="status WAITING"></span>{{ $t("waiting") }}</span>
                <span><span class="status FAILED"></span>{{ $t("failure") }}</span>
            </div>
        </template>
        <template v-slot:duration="{row}">
            <div>{{ calculateDuration(row) }}</div>
        </template>
        <template v-slot:state="{row}">
            <div width="10" class="status" :class="{[row.state]: true}">-</div>
        </template>
        <template v-slot:view="{row}">
            <span class="command-edit" @click="itemsStore.taskID = row.task_id">{{ $t("view") }}</span>
        </template>
        <template v-slot:write-traceback="value">
            <div class="traceback">{{ value["value"] }}</div>
        </template>
        <template v-slot:write-logs_link="{form}">
            <el-link :href="`/ray/#/jobs/${form.job_id}/tasks/${form.task_id}`" target="_blank">Ray logs</el-link>
        </template>
        <template v-slot:write-creation_time_ms="value">
            <span class="field-name">{{ $t("creation_time_ms") }}</span>{{
                formatDate(value["value"])
            }}
        </template>
        <template v-slot:write-start_time_ms="value">
            <span class="field-name">{{ $t("start_time_ms") }}</span>{{ formatDate(value["value"]) }}
        </template>
        <template v-slot:write-end_time_ms="value">
            <span class="field-name">{{ $t("end_time_ms") }}</span>{{ formatDate(value["value"]) }}
        </template>
        <template v-slot:write-events="value">
            <el-collapse accordion @click="(ev) => ev.preventDefault()">
                <el-collapse-item>
                    <template #title>
                        <span class="field-name">{{ $t('events') }}</span>
                    </template>
                    <div class="json-field">
                        {{ JSON.stringify(value["value"], null, 4) }}
                    </div>
                </el-collapse-item>
            </el-collapse>
        </template>
        <template v-slot:write-profiling_data="value">
            <el-collapse accordion @click="(ev) => ev.preventDefault()">
                <el-collapse-item>
                    <template #title>
                        <span class="field-name">{{ $t('profiling_data') }}</span>
                    </template>
                    <div class="json-field">
                        {{ JSON.stringify(value["value"], null, 4) }}
                    </div>
                </el-collapse-item>
            </el-collapse>
        </template>
        <template v-slot:write-runtime_env_info="value">
            <el-collapse accordion @click="(ev) => ev.preventDefault()">
                <el-collapse-item>
                    <template #title>
                        <span class="field-name">{{ $t('runtime_env_info') }}</span>
                    </template>
                    <div class="json-field">
                        {{ JSON.stringify(value["value"], null, 4) }}
                    </div>
                </el-collapse-item>
            </el-collapse>
        </template>


    </ReadWriteView>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";

const password = ref(null)

const itemsStore = useItemsStore()

const itemType = ref("tasks")
await itemsStore.loadSchema()


function calculateDuration({start_time_ms, end_time_ms}) {
    // Calculate duration in mili, secs, minutes or hours depending on the diration itself, format of imput dates are: 2023-12-11T16:08:44.661922
    if (start_time_ms && end_time_ms) {
        const dateCreated = new Date(start_time_ms)
        const dateFinished = new Date(end_time_ms)
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

function formatDate(creation_time_ms) {
    if (creation_time_ms) {
        const dateObj = new Date(creation_time_ms)
        return `${dateObj.getDate()}/${dateObj.getMonth() + 1}/${dateObj.getFullYear()} ${dateObj.getHours()}:${dateObj.getMinutes()}:${dateObj.getSeconds()}`
    } else {
        return null
    }
}


function sortDates(a, b) {
    const dateA = new Date(a.creation_time_ms)
    const dateB = new Date(b.creation_time_ms)
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

function timeMSFormatter(row, propName) {
    return formatDate(row[propName])
}

function durationMSFormatter(row, propName) {
    return calculateDuration(row)
}

</script>
<style lang="scss" scoped>
.status {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin: 0 auto;
    // &.NIL, &.PENDING_ARGS_AVAIL, &.PENDING_NODE_ASSIGNMENT, &.PENDING_OBJ_STORE_MEM_AVAIL, &.PENDING_ARGS_FETCH, &.SUBMITTED_TO_WORKER
    background-color: #F2C94C; // waiting

    &.FINISHED {
        background-color: #27AE60;
    }

    &.FAILED {
        background-color: #EB5757;
    }

    &.RUNNING, &.RUNNING_IN_RAY_GET, &.RUNNING_IN_RAY_WAIT {
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
.json-field {
    white-space: pre-wrap;
    padding: 10px;
    background-color: #f5f5f5;
    border-radius: 5px;
    margin-top: 10px;
    margin-bottom: 10px;
    font-size: 12px;
    font-family: monospace;
    color: #333;
    overflow: auto;
    max-height: 500px;
}
.field-name {
    color: var(--chatfaq-color-primary-500);
    font-size: 14px;
    font-weight: 600;
    line-height: 20px;
    letter-spacing: 0em;
    text-align: left;
    margin-right: 8px;
}
</style>
