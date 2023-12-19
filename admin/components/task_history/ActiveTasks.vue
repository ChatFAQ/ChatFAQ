<template>
    <div v-if="itemsStore.items[apiUrl] && itemsStore.items[apiUrl].length" class="active-tasks"
         @click="opened = !opened">
        <div class="active-tasks-header">
            <span>{{ $t("numberofactivetasks", {number: itemsStore.items[apiUrl].length}) }}</span>
            <el-icon>
                <ArrowUp v-if="opened"/>
                <ArrowDown v-else/>
            </el-icon>
        </div>
        <div class="active-tasks-body" v-if="opened">
            <div v-for="item in itemsStore.items[apiUrl]" :key="item.id" class="active-task">
                <div class="active-task-name">{{ formatTaskName(item.task_name) }}</div>
                <div class="active-task-status" v-if="item.status !== 'STARTED'">{{ formatState(item.status) }}</div>
                <div class="active-task-status" v-else-if="item.status">56% 3H Remaining</div>
                <div class="active-task-progress">
                    <el-progress v-if="item.status === 'STARTED'" :percentage="50" :show-text="false" :stroke-width="6"
                                 :color="getColor(item.status)"></el-progress>
                    <el-progress v-else :percentage="100" :show-text="false" :stroke-width="6"
                                 :color="getColor(item.status)"></el-progress>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import {ArrowDown, ArrowUp} from "@element-plus/icons-vue";

const numberOfActiveTasks = ref(1)
let ws = undefined
const itemsStore = useItemsStore()
const apiUrl = ref("/back/api/language-model/tasks/")
const opened = ref(false)
if (process.client)
    createConnection()

function createConnection() {
    if (ws)
        ws.close()

    ws = new WebSocket(
        "ws://localhost:8000"
        + "/back/ws/broker/tasks/?token="
        + useCookie('token').value
    );
    ws.onmessage = async function (e) {
        const msg = JSON.parse(e.data);
        if (msg.status === 400) {
            console.error(`Error in message from WS: ${msg.payload}`)
            return
        }

        itemsStore.items[apiUrl.value] = msg
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

function formatTaskName(taskName) {
    if (!taskName)
        return ""
    return taskName.split(".")[taskName.split(".").length - 1]
}

function getColor(status) {
    if (status === "SUCCESS")
        return "#27AE60"
    else if (status === "FAILURE")
        return "#EB5757"
    else if (status === "STARTED")
        return "#2D9CDB"
    else if (status === "WAITING")
        return "#F2C94C"
    else
        return "#F2C94C"
}

function formatDate(date) {
    if (date) {
        const dateObj = new Date(date)
        return `${dateObj.getDate()}/${dateObj.getMonth() + 1}/${dateObj.getFullYear()} ${dateObj.getHours()}:${dateObj.getMinutes()}:${dateObj.getSeconds()}`
    } else {
        return null
    }
}
function formatState(state) {
    // uppercase only firt cahracter:
    state = state.charAt(0).toUpperCase() + state.slice(1).toLowerCase()
    if (state === "Success")
        return "100% " + state
    else if (state === "Failure")
        return state
    else if (state === "Started")
        return "56% 3h remaining"  // TODO
    else if (state === "Waiting")
        return state
    else
        return state
}

</script>
<style lang="scss" scoped>
.active-tasks {
    width: 330px;

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

        > * {
            margin-bottom: 8px;
        }
    }

    .active-tasks-body {
        max-height: 400px;
        overflow-y: scroll;
    }

    .active-task-name {
        font-size: 14px;
        font-weight: 600;
        line-height: 20px;
        letter-spacing: 0em;
        text-align: left;

    }
}
</style>
