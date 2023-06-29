<template>
    <div class="separator-line"></div>
    <div class="references-wrapper">
        <div class="references-title-wrapper">
            <div class="references-title">{{ $t('summarygeneratedfrom') }}</div>
            <div v-if="collapsed" class="collapsed-references purple-background" @click="collapsed = !collapsed">
                +{{ references.length }} {{ $t('sources') }}
            </div>
        </div>
        <div class="references" v-if="!collapsed">
            <div class="reference purple-background" v-for="ref in references"><a :href="ref.url" target="_blank">{{ ref.url_title ? ref.url_title : ref.url }}</a></div>
        </div>
    </div>
</template>

<script setup>

const props = defineProps(["references"]);
const collapsed = ref(true);


</script>
<style scoped lang="scss">
    @import "assets/styles/variables";

    .references-title-wrapper {
        display: flex;
        flex-direction: row;
        align-items: center;
        margin-bottom: 8px;

        .references-title {
            font-style: italic;
            line-height: 20px;
            color: $chatfaq-color-neutral-purple;
        }
        .collapsed-references {
            margin-left: 8px;
            color: $chatfaq-color-primary-500;
            cursor: pointer;

        }
    }
    .separator-line {
        height: 1px;
        background-color: rgba(70, 48, 117, 0.2);
        align-content: center;
        text-align: center;
        margin-top: 8px;
        margin-bottom: 8px;
        &.dark-mode {
            background-color: $chatfaq-color-neutral-purple;
        }
    }
    .purple-background {
        background: rgba(70, 48, 117, 0.1);
        border-radius: 4px;
        padding: 2px 6px 2px 6px;
    }
    .reference {
        margin-bottom: 8px;
        margin-right: 8px;
        width: fit-content;

        a {
            text-decoration: none;
            color: #463075;
        }
    }
</style>
