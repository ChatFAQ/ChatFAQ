<template>
    <div v-if="items && items.length" class="active-tasks">
        <div class="active-tasks-header" @click="opened = !opened">
            <span>{{ $t("numberofactivetasks", {number: items.length}) }}</span>
            <el-icon>
                <ArrowUp v-if="opened"/>
                <ArrowDown v-else/>
            </el-icon>
        </div>
        <div class="active-tasks-body" v-if="opened">
            <div v-for="item in items" :key="item.task_id" class="active-task" @click="goToTaskToDetail(item.task_id)">
                <div class="active-task-name">
                    <span class="name">{{ formatTaskName(item.name) }}</span>
                    <span v-if="item.state !== 'WAITING'" class="action" @click.stop @click="removeItem(item.task_id)">{{ $t("close") }}</span>
                </div>
                <div class="active-task-state" v-if="item.state !== 'STARTED'">{{ formatState(item.state) }}</div>
                <div class="active-task-state" v-else-if="item.state">{{ $t("inprogress") }}</div>
                <div class="active-task-progress">
                    <el-progress v-if="RUNNING_STATUSES.indexOf(item.state) > -1" :percentage="50" :show-text="false" :stroke-width="6"
                                 :color="getColor(item.state)"><span>{{ $t("inprogress") }}</span></el-progress>
                    <el-progress v-else :percentage="100" :show-text="false" :stroke-width="6"
                                 :color="getColor(item.state)"></el-progress>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import {ArrowDown, ArrowUp} from "@element-plus/icons-vue";
import {useI18n} from "vue-i18n";

let ws = undefined
const itemsStore = useItemsStore()
const items = ref([])
const lastItemDate = ref(new Date())
const apiUrl = ref("/back/api/language-model/tasks/")
const opened = ref(false)
const router = useRouter();
const conf = useRuntimeConfig()
const { t } = useI18n();

const { $useRay } = useNuxtApp()

const WAITING_STATUSES = ["NIL", "PENDING_ARGS_AVAIL", "PENDING_NODE_ASSIGNMENT", "PENDING_OBJ_STORE_MEM_AVAIL", "PENDING_ARGS_FETCH", "SUBMITTED_TO_WORKER"]
const RUNNING_STATUSES = ["RUNNING", "RUNNING_IN_RAY_GET", "RUNNING_IN_RAY_WAIT"]


if (process.client && $useRay)
    createConnection()

function createConnection() {
    if (ws)
        ws.close()

    ws = new WebSocket(
        conf.public.chatfaqWS
        + "/back/ws/broker/tasks/?token="
        + useCookie('token').value
    );
    ws.onmessage = async function (e) {
        const msg = JSON.parse(e.data);
        if (msg.state === 400) {
            console.error(`Error in message from WS: ${msg.payload}`)
            return
        }
        setItems(msg)
    };
    ws.onopen = function (e) {
        // createHeartbeat(ws)
    };
    ws.onclose = function (e) {
        setTimeout(function () {
            createConnection();
        }, 1000);
        // deleteHeartbeat()
    };
}

function setItems(newItems) {
    // Update items.value
    // If lastItemDate.value is null the only add items that are WAITING or STARTED
    // If lastItemDate.value is not null add all new items that are newer than lastItemDate.value
    // Update lastItemDate.value
    const filteredItems = newItems.filter(item => new Date(item.date_created) >= lastItemDate.value - 1000 || WAITING_STATUSES.indexOf(item.state) > -1 || RUNNING_STATUSES.indexOf(item.state) > -1)
    // add pendingNewItems if they dont exists yet
    filteredItems.forEach(filteredItem => {
        if (!items.value.find(item => item.task_id === filteredItem.task_id))
            items.value.push(filteredItem)
    })
    // Update the exisitng items with the new items by id
    items.value = items.value.map(item => {
        const newItem = newItems.find(newItem => newItem.task_id === item.task_id)
        if (newItem)
            return newItem
        else
            return item
    })
    lastItemDate.value = new Date()

}

function removeItem(id) {
    items.value = items.value.filter(item => item.task_id !== id)
}

function goToTaskToDetail(id) {
    itemsStore.taskID = id
    router.push('/task_history');
}

function formatTaskName(taskName) {
    if (!taskName)
        return ""
    return taskName.split(".")[taskName.split(".").length - 1]
}

function getColor(state) {
    if (state === "FINISHED")
        return "#27AE60"
    else if (state === "FAILED")
        return "#EB5757"
    else if (RUNNING_STATUSES.indexOf(state) > -1)
        return "#2D9CDB"
    else if (WAITING_STATUSES.indexOf(state) > -1)
        return "#F2C94C"
    else
        return "#F2C94C"
}

function formatState(state) {
    // uppercase only firt cahracter:
    state = state.charAt(0).toUpperCase() + state.slice(1).toLowerCase()
    if (state === "Success")
        return "100% " + state
    else if (state === "Failure")
        return state
    else if (state === "Started")
        return t("inprogress")
    else if (state === "Waiting")
        return state
    else
        return state
}

</script>
<style lang="scss" scoped>
.active-tasks {
    z-index: 3;
    width: 330px;
    box-shadow: 0px 0px 12px 0px #0000001F;

    .active-tasks-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 60px;
        background-color: $chatfaq-color-primary-500;
        border-radius: 4px;
        padding: 16px 24px 16px 24px;
        color: white;
        cursor: pointer;
    }

    .active-task {
        padding: 16px;
        cursor: pointer;

        > * {
            margin-bottom: 8px;
        }
    }

    .active-tasks-body {
        max-height: 400px;
        overflow-y: scroll;
    }

    .active-task-name {
        display: flex;
        justify-content: space-between;

        .action {
            font-size: 12px;
            font-weight: 400;
            color: #8E959F;
            cursor: pointer;
            &:hover {
                text-decoration: underline;
            }

        }

        .name {
            font-size: 14px;
            font-weight: 600;
            line-height: 20px;
        }

    }
}
</style>
