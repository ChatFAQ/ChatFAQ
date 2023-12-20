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
            <div v-for="item in items" :key="item.id" class="active-task" @click="goToTaskToDetail(item.id)">
                <div class="active-task-name">
                    <span class="name">{{ formatTaskName(item.task_name) }}</span>
                    <span v-if="item.status !== 'WAITING'" class="action" @click="removeItem(item.id)">Close</span>
                </div>
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

let ws = undefined
const itemsStore = useItemsStore()
const items = ref([])
const lastItemDate = ref()
const apiUrl = ref("/back/api/language-model/tasks/")
const opened = ref(false)
const router = useRouter();

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
    if (lastItemDate.value) {
        const newItemsFiltered = newItems.filter(item => new Date(item.date_created) > lastItemDate.value)
        items.value = items.value.concat(newItemsFiltered)
    } else {
        const newItemsFiltered = newItems.filter(item => item.status === "WAITING" || item.status === "STARTED")
        items.value = items.value.concat(newItemsFiltered)
    }
    // Update the exisitng items with the new items by id
    items.value = items.value.map(item => {
        const newItem = newItems.find(newItem => newItem.id === item.id)
        if (newItem)
            return newItem
        else
            return item
    })
    lastItemDate.value = new Date()

}

function removeItem(id) {
    items.value = items.value.filter(item => item.id !== id)
}

function goToTaskToDetail(id) {
    itemsStore.editing = id
    router.push('/task_history');
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
            color: grey;
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
