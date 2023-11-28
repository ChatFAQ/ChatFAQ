<template>
    <div class="color-field">
        <el-color-picker v-model="colorValue" size="large"/>
        <el-input v-model="colorValue"/>
    </div>
</template>

<script setup>
const {$axios} = useNuxtApp();

const props = defineProps({
    field: {
        type: Object,
        mandatory: true
    },
})

const colorValue = computed({
    get() {
        if (props.field.values)
            return props.field.values.light
        return props.field.value
    },
    set(newValue) {
        if (props.field.values) {
            props.field.values.light = newValue
        } else {
            props.field.value = newValue
        }
    }
})

</script>

<style lang="scss">
.color-field {
    display: flex;

    .el-color-picker__trigger {
        margin-right: 16px;

        .el-color-picker__color {
            border-radius: 6px;
            .el-color-picker__color-inner {
                border-radius: 5px;

            }
        }
    }
}

</style>
