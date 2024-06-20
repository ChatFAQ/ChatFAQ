<template>
    <client-only>
        <Suspense>
            <template #default>
                <TaskHistory/>
            </template>
            <template #fallback>
                <div class="main-component-page-loader" v-loading="true" />
            </template>
        </Suspense>
    </client-only>
</template>

<script setup>
import TaskHistory from "~/components/task_history/TaskHistory.vue";

</script>
