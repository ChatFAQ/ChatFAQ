<template>
    <svg v-if="_modelValue" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="checkbox" @click="change">
        <g clip-path="url(#clip0_174_112)">
            <rect x="1" y="1" width="14" height="14" rx="4" fill="#DFDAEA" fill-opacity="0.1"/>
            <path d="M4.5 8L6.97487 10.4749L11.9246 5.52512" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                  stroke-linejoin="round"/>
        </g>
        <rect x="1.5" y="1.5" width="13" height="13" rx="3.5" stroke="currentColor"/>
        <defs>
            <clipPath id="clip0_174_112">
                <rect x="1" y="1" width="14" height="14" rx="4" fill="currentColor"/>
            </clipPath>
        </defs>
    </svg>

    <div v-else class="unchecked">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="checkbox non-ghost" @click="change">
            <g clip-path="url(#clip0_174_110)">
            </g>
            <rect x="1.5" y="1.5" width="13" height="13" rx="3.5" stroke="currentColor"/>
            <defs>
                <clipPath id="clip0_174_110">
                    <rect x="1" y="1" width="14" height="14" rx="4" fill="currentColor"/>
                </clipPath>
            </defs>
        </svg>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="checkbox ghost" @click="change">
            <g clip-path="url(#clip0_174_112)">
                <rect x="1" y="1" width="14" height="14" rx="4" fill="#DFDAEA" fill-opacity="0.1"/>
                <path d="M4.5 8L6.97487 10.4749L11.9246 5.52512" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                      stroke-linejoin="round" class="ghosted"/>
            </g>
            <rect x="1.5" y="1.5" width="13" height="13" rx="3.5" stroke="currentColor"/>
            <defs>
                <clipPath id="clip0_174_112">
                    <rect x="1" y="1" width="14" height="14" rx="4" fill="currentColor"/>
                </clipPath>
            </defs>
        </svg>
    </div>
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
    min-width: 16px;
    &.dark {
        fill: $chatfaq-color-primary-500;
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
            .ghosted {
                opacity: 0.5;
            }
        }
        .non-ghost {
            display: none;
        }
    }
}

</style>


