<template>
    <div class="color-field">
        <el-color-picker v-model="firstGradient" size="large" show-alpha/>
        <el-color-picker v-model="secondGradient" size="large" show-alpha/>
        <span class="hex-preview">{{pretty()}}</span>
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
function parseGradient(gradient) {
    const alphaColors = gradient.match(/#(?:[0-9a-f]{3}){1,2}[0-9a-f]{2}/gi)
    if (alphaColors.length)
        return alphaColors
    return gradient.match(/#(?:[0-9a-f]{3}){1,2}/gi)
}
const firstGradient = ref(parseGradient(props.field.value)[0])
const secondGradient = ref(parseGradient(props.field.value)[1])

function pretty() {
    return `${rgba2hex(firstGradient.value)} to ${rgba2hex(secondGradient.value)}`
}
function getValue() {
    return `linear-gradient(135deg, ${rgba2hex(firstGradient.value)} 0%, ${rgba2hex(secondGradient.value)} 100%)`
}
</script>

<style lang="scss">
.color-field {
    display: flex;
    align-items: center;

    .el-color-picker {
        width: unset !important;
    }
    .el-color-picker__trigger {
        margin-right: 16px;

        .el-color-picker__color {
            border-radius: 6px;
            .el-color-picker__color-inner {
                border-radius: 5px;

            }
        }
    }
    .hex-preview {
        color: $chatfaq-color-greyscale-800;
    }
}

</style>
