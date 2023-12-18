<template>
    <el-tabs @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :lazy="true" name="tasks">
            <ReadWriteView
                apiUrl="/back/api/language-model/tasks/"
                :readOnly="true"
                :tableProps="{
                    'status': '',
                    'task_name': $t('task_name'),
                    'date_created': $t('date_created'),
                    'duration': $t('duration'),
                }">
                <template v-slot:duration="{row}">
                    <div>{{calculateDuration(row)}}</div>
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
import { useItemsStore } from "~/store/items.js";

const password = ref(null)

const { $axios } = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("tasks")
await itemsStore.loadSchema($axios)


function calculateDuration({date_created, date_done}) {
    // Calculate duration in mili, secs, minutes or hours depending on the diration itself, format of imput dates are: 2023-12-11T16:08:44.661922
    if (date_done) {
        const dateCreated = new Date(date_created)
        const dateFinished = new Date(date_done)
        const diff = dateFinished - dateCreated
        if (diff < 1000) {
            return `${diff} ms`
        } else if (diff < 60000) {
            return `${diff / 1000} s`
        } else if (diff < 3600000) {
            return `${diff / 60000} min`
        } else {
            return `${diff / 3600000} h`
        }
    } else {
        return null
    }
}
</script>
<style lang="scss" scoped>
.status {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin: 0 auto;
    background-color: #F2C94C;  // waiting

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
</style>
