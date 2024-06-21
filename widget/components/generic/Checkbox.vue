<template>
    <CheckboxChecked v-if="_modelValue" @click="change" class="checkbox" />
    <div v-else class="unchecked">
        <Checkbox @click="change" class="checkbox non-ghost"/>
        <CheckboxHover  class="checkbox ghost" @click="change"/>
    </div>
</template>


<script setup>
import {ref, watch, defineEmits} from "vue";
import Checkbox from "~/components/icons/Checkbox.vue";
import CheckboxChecked from "~/components/icons/CheckboxChecked.vue";
import CheckboxHover from "~/components/icons/CheckboxHover.vue";

const props = defineProps(["modelValue", "dark", "notReactive"]);
const emit = defineEmits(['update:modelValue'])
const _modelValue = ref(props.modelValue);
_modelValue.value = false;
watch(() => props.modelValue, (value) => {
    _modelValue.value = value;
})
function change() {
    if (props.notReactive)
        return;
    _modelValue.value = !_modelValue.value
    emit('update:modelValue', _modelValue.value)
}

</script>

<style lang="scss" scoped>

.checkbox {
    min-width: 16px;
    color: $chatfaq-check-icon-color-light;
    &.dark {
        color: $chatfaq-check-icon-color-dark;
    }
}
.unchecked {
    .ghost {
        display: none;
    }
    display: contents;
    &:hover {
        .ghost {
            display: block;
        }
        .non-ghost {
            display: none;
        }
    }
}

</style>


