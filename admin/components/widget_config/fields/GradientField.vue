<template>
    <div class="gradinet-color-field">
        <div class="gradients-picker">
            <div class="gradient">
                <el-color-picker v-model="firstGradient" size="large" show-alpha  @change="firstGradient = rgba2hex(firstGradient)"/>
                <el-input v-model="firstGradient" size="large" class="hex-input" placeholder="Hex color" @change="firstGradient = rgba2hex(firstGradient)"/>
            </div>
            <div class="gradient">
                <el-color-picker v-model="secondGradient" size="large" show-alpha  @change="secondGradient = rgba2hex(secondGradient)"/>
                <el-input v-model="secondGradient" size="large" class="hex-input" placeholder="Hex color" @change="secondGradient = rgba2hex(secondGradient)"/>
            </div>
        </div>
        <div class="gradient-visualizer-wrapper">
            <div class="gradient-visualizer">
                <div class="gradient-visualizer-inside">
                    <div :style="{background: getValue()}"></div>
                </div>
            </div>
            <span class="hex-preview">{{ pretty() }}</span>
        </div>
    </div>
</template>

<script setup>
import {rgba2hex} from '~/utils'

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
    const alphaColors = gradient.match(/#(?:[0-9a-f]{6})[0-9a-f]{2}/gi)
    if (alphaColors !== null)
        return alphaColors
    return gradient.match(/#(?:[0-9a-f]{6})/gi)
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
.gradinet-color-field {
    display: flex;
    flex-direction: column;

    .gradients-picker {
        display: flex;
        align-items: center;
        flex-direction: column;
        .gradient {
            margin-bottom: 8px;
        }
        .el-color-picker {
            width: unset !important;
        }

        .el-color-picker__trigger {
            margin-right: 16px;
            border-radius: 10px;

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

    .gradient-visualizer-wrapper {
        display: flex;
        align-items: center;

        .gradient-visualizer {
            width: 40px;
            height: 40px;
            border: 1px solid var(--el-border-color);
            border-radius: 10px;
            display: flex;

            .gradient-visualizer-inside {
                width: 30px;
                height: 30px;
                border: 1px solid var(--el-border-color);
                border-radius: 6px;
                display: flex;
                margin: auto;

                div {
                    width: 28px;
                    height: 28px;
                    border-radius: 5px;
                    margin: auto;

                }
            }
        }

        .hex-preview {
            margin-left: 16px;
            color: $chatfaq-color-greyscale-800;
        }
    }

    .hex-input {
        width: 110px;

    }
}

</style>
