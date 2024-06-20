<template>
    <client-only>
        <Suspense>
            <template #default>
                <Labeling/>
            </template>
            <template #fallback>
                <div class="main-component-page-loader" v-loading="true" />
            </template>
        </Suspense>
    </client-only>
</template>

<script setup>
import Labeling from "~/components/labeling/Labeling.vue";
</script>
