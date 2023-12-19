<template>
    <el-tabs @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :lazy="true" name="tasks">
            <ReadWriteView
                apiUrl="/back/api/language-model/tasks/"
                :readOnly="true"
                :readable-name='$t("asynctasks")'
                :tableProps="{
                    'status': {'name': '', 'width': 50},
                    'task_name': {'name': $t('task_name')},
                    'date_created': {'name': $t('date_created')},
                    'duration': {'name': $t('duration')},
                    'view': {'name': $t('duration')},
                }">
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
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
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
</style>
