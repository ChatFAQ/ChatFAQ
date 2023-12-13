<template>
    <div class="font-field">
        <div class="preview" :style="{font: getValue()}">Aa</div>
        <el-input v-model="field.value"/>
    </div>
</template>

<script setup>
import { rgba2hex } from '~/utils'

defineExpose({
    getValue,
})
const props = defineProps({
    field: {
        type: Object,
        mandatory: true
    },
})


function getValue() {
    return props.field.value
}
</script>

<style lang="scss" scoped>
.font-field {
    display: flex;
    align-items: center;
}
.preview {
    min-width: 64px !important;
    height: 64px;
    border-radius: 10px;
    background-color: $chatfaq-color-primary-200;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24px;
    max-font-size: 20px !important;
    overflow: hidden;
    border: 1px dotted #DFDAEA66;
}
</style>
