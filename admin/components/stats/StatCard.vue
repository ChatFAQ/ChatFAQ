<template>
<div class="stat-card-wrapper">
    <div v-if="typeof content === 'number'">
        <div class="stat-title">{{title}}</div>
        <div class="stat-content">{{content}}<span v-if="type == 'percentage'">%</span></div>
    </div>
    <div v-else class="table-wrapper">
        <div class="stat-title">{{title}}</div>
        <div class="table">
            <el-table :data="content"
                      :stripe="false"
                      style="width: 100%">
                <el-table-column
                    v-for="prop in tableProps"
                    :prop="prop"
                    :label="$t(prop)"
                    :sortable="true"
                >
                </el-table-column>
            </el-table>
        </div>
    </div>
</div>
</template>

<script setup>

import { ref, watch, defineProps } from 'vue'

// attribute props
const props = defineProps({
    title: {
        type: String,
        required: true
    },
    content: {
        type: [Number, Object],
        required: true
    },
    type: {
        type: String,
        required: false
    }
});

const tableProps = computed(() => {
    if (props.content === undefined)
        return []
    if (Array.isArray(props.content))
        return Object.keys(props.content[0])
    return []
})

</script>

<style lang="scss" scoped>
.stat-card-wrapper {
    max-height: 200px;
    padding: 24px;
    border-radius: 10px;
    border: 1px;
    gap: 24px;
    border: 1px solid $chatfaq-color-primary-200;
    background: #FFFFFF99;
    .stat-title {
        font-size: 14px;
        font-weight: 400;
        color: $chatfaq-color-neutral-black;
        margin-bottom: 8px;
    }
    .stat-content {
        //styleName: Title/SM/Bold;
        font-family: Montserrat;
        font-size: 24px;
        font-weight: 700;
        color: $chatfaq-color-neutral-black;
    }
    .table-wrapper {
        display: flex;
        flex-direction: column;
        .table {
            overflow-y: auto;
            height: 125px;
        }
    }
}
</style>
