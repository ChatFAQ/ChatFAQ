<template>
    <div class="separator-line" :class="{ 'dark-mode': store.darkMode }"></div>
    <div class="references-wrapper">
        <div class="references-title-wrapper">
            <div class="references-title" :class="{ 'dark-mode': store.darkMode }">{{ $t('summarygeneratedfrom') }}
            </div>
            <div
                class="collapsed-references-button purple-background"
                @click="collapsed = !collapsed"
                :class="{ 'dark-mode': store.darkMode, 'sources-first': store.sourcesFirst }"
            >
                <span v-if="collapsed">{{ (references?.knowledge_items || []).length }} <span v-if="(references?.knowledge_items || []).length === 1">{{ $t('source') }}</span> <span v-else>{{ $t('sources') }}</span></span>
                <span v-else>{{ $t('showless') }}</span>
                <ArrowDownCircle v-if="collapsed"/>
                <ArrowUpCircle v-else/>
            </div>
        </div>
        <div class="references" v-if="!collapsed">
            <div
                class="reference purple-background"
                v-for="(ref, index) in references?.knowledge_items || []"
                :class="{
                    'dark-mode': store.darkMode
                }">
                    <a :href="ref.url" target="_blank">{{ index + 1 }}. {{
                        ref.title ? ref.title : ref.url
                    }}</a>
            </div>
        </div>
    </div>
</template>

<script setup>

import { useGlobalStore } from "~/store";
import {ref} from "vue";
import ArrowDownCircle from "~/components/icons/ArrowDownCircle.vue";
import ArrowUpCircle from "~/components/icons/ArrowUpCircle.vue";

const props = defineProps(["references"]);
const store = useGlobalStore();
const collapsed = ref(!store.sourcesFirst);


</script>
<style scoped lang="scss">

.references-title-wrapper {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-bottom: 8px;

    .references-title {
        font-style: italic;
        line-height: 20px;
        color: $chatfaq-color-chatMessageReferenceTitle-text-light;
        &.dark-mode {
            color: $chatfaq-color-chatMessageReferenceTitle-text-dark;
        }
    }

    .collapsed-references-button {
        margin-left: 8px;
        color: $chatfaq-color-chatMessageReference-text-light;
        cursor: pointer;
        font-size: 12px;
        display: flex;
        align-items: center;
        &.dark-mode {
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
        svg {
            margin-left: 4px;
        }
        &.sources-first {
            display: none;
        }

    }
}

.separator-line {
    height: 1px;
    background-color: $chatfaq-color-separator-light;
    align-content: center;
    text-align: center;
    margin-top: 8px;
    margin-bottom: 8px;

    &.dark-mode {
        background-color: $chatfaq-color-separator-dark;
    }
}

.purple-background {
    background: $chatfaq-color-chatMessageReference-background-light;
    border-radius: 4px;
    padding: 2px 6px 2px 6px;
    &.dark-mode {
        background: $chatfaq-color-chatMessageReference-background-dark;
    }
}

.reference {
    margin-bottom: 8px;
    margin-right: 8px;
    width: fit-content;
    a {
        text-decoration: none;
        color: $chatfaq-color-chatMessageReference-text-light;
    }
    &.dark-mode {
        a {
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
    }
}
</style>
