<template>
    <div class="labeling-tool-wrapper">
        <div class="labeling-tool-left-side">
            <div @click="setQAPairToLabel(msgs[msgs.length - 1].id)"
                 v-for="msgs in getQAMessageGroups(conversation.mml_chain)" class="qa-group">
                <div v-for="msg in msgs" class="message" :class="{[msg.sender.type]: true}">
                    {{
                        typeof (msg.stack[0].payload) === 'string' ? msg.stack[0].payload : msg.stack[0].payload.model_response
                    }}
                </div>
            </div>
        </div>
        <div class="labeling-tool-right-side">
            <el-tabs>
                <el-tab-pane :lazy="true" :label="$t('knowledgeitems')" name="knowledge-items">
                    {{ msgLabeled }}
                </el-tab-pane>
                <el-tab-pane :lazy="true" :label="$t('givefeedback')" name="give-feedback">
                    {{ msgLabeled }}
                </el-tab-pane>
                <el-tab-pane :lazy="true" :label="$t('usersfeedback')" name="users-feedback">
                    {{ msgLabeled }}
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const router = useRouter()

const {$axios} = useNuxtApp()

const msgLabeled = ref(undefined)

const props = defineProps({
    id: {
        type: String,
        mandatory: true
    },
})

// get conversation async data
const {data} = await useAsyncData(
    "conversation" + props.id,
    async () => await $axios.get("/back/api/broker/conversations/" + props.id + "/")
)

const conversation = ref(data.value.data)

function getQAMessageGroups(MMLChain) {
    let groups = []
    let group = []
    for (let i = 0; i < MMLChain.length; i++) {
        if (MMLChain[i].sender.type === 'bot') {
            group.push(MMLChain[i])
            groups.push(group)
            group = []
        } else {
            group.push(MMLChain[i])
        }
    }
    return groups
}

function setQAPairToLabel(id) {
    msgLabeled.value = id
}

</script>

<style lang="scss">
.el-tabs {
    margin-left: 24px;
    margin-right: 24px;
}

.el-tabs__nav {
    float: unset;
    justify-content: space-between;
}
</style>
<style lang="scss" scoped>
.labeling-tool-wrapper {
    display: flex;
    flex-direction: row;
    margin-right: 60px;

    .labeling-tool-left-side, .labeling-tool-right-side {
        border-radius: 10px;
        background: white;
        border: 1px solid #DFDAEA;
        max-height: 70vh;
        overflow-y: auto;
        padding-top: 16px;
    }

    .labeling-tool-left-side {
        flex: 1.75;
        margin-right: 12px;
    }

    .labeling-tool-right-side {
        flex: 1.25;
        margin-left: 12px;
    }

    .qa-group {
        position: relative;
        padding: 9px 28px;

        &:hover {
            background: #DFDAEA;
            cursor: pointer;
        }

        .message {
            border-radius: 6px;
            max-width: 400px;
            padding: 8px 12px 8px 12px;
            margin-bottom: 8px;
            width: 100%;

            display: block;
            overflow: auto;

            &.bot {
                background: #46307524;
            }

            &.human {
                background: $chatfaq-color-primary-500;
                float: right;
                color: white;
            }
        }
    }
}
</style>

