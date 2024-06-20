<template>
    <client-only>
        <Suspense>
            <template #default>
                <AIConfig/>
            </template>
            <template #fallback>
                <div class="main-component-page-loader" v-loading="true"/>
            </template>
        </Suspense>
    </client-only>
</template>

<script setup>
import AIConfig from "~/components/ai_config/AIConfig.vue";
</script>
