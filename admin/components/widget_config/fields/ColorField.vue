<template>
    <div class="color-field">
        <el-color-picker v-model="colorValue" size="large" show-alpha/>
        <span class="hex-preview">{{rgba2hex(colorValue).toUpperCase()}}</span>
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

const colorValue = computed({
    get() {
        if (props.field.value.light)
            return props.field.value.light
        return props.field.value
    },
    set(newValue) {
        if (props.field.value.light) {
            props.field.value.light = newValue
        } else {
            props.field.value = newValue
        }
    }
})

function getValue() {
    return props.field.value
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
