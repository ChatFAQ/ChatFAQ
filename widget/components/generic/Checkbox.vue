<template>
    <i class="checkbox" :class="{'checked': _modelValue, 'dark': dark}" @click="change"/>
</template>


<script setup>
import {defineEmits} from 'vue';

const props = defineProps(["modelValue", "dark"]);
const emit = defineEmits(['update:modelValue'])
const _modelValue = ref(props.modelValue);
_modelValue.value = false;

function change() {
    _modelValue.value = !_modelValue.value
    emit('update:modelValue', _modelValue.value)
}

</script>

<style lang="scss" scoped>
@import "assets/styles/variables";

.checkbox {
    content: $chatfaq-checkbox-icon;

    &.checked {
        content: $chatfaq-checkbox-checked-icon;
    }
    &.dark {
        fill: black;
        color: black;
    }

}

</style>


