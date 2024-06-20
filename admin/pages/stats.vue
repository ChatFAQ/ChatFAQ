<template>
    <client-only>
        <Suspense>
            <template #default>
                <Stats/>
            </template>
            <template #fallback>
                <div class="main-component-page-loader" v-loading="true" />
            </template>
        </Suspense>
    </client-only>
</template>

<script setup>
import Stats from "~/components/stats/Stats.vue";

</script>
