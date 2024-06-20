<template>
    <Suspense>
        <template #default>
            <Data/>
        </template>
        <template #fallback>
            <div class="main-component-page-loader" v-loading="true" />
        </template>
    </Suspense>
</template>

<script setup>
import Data from "~/components/data/Data.vue";
</script>
