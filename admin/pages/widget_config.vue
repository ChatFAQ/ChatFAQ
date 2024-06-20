<template>
    <client-only>
        <Suspense>
            <template #default>
                <WidgetConfig/>
            </template>
            <template #fallback>
                <div class="main-component-page-loader" v-loading="true" />
            </template>
        </Suspense>
    </client-only>
</template>

<script setup>
import WidgetConfig from "~/components/widget_config/WidgetConfig.vue";
</script>
