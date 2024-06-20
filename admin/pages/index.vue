<template>
    <client-only>
        <Suspense>
            <template #default>
                <Dashboard/>
            </template>
            <template #fallback>
                <div class="main-component-page-loader" v-loading="true" />
            </template>
        </Suspense>
    </client-only>
</template>

<script setup>
import Dashboard from "~/components/dashboard/Dashboard.vue";

</script>

