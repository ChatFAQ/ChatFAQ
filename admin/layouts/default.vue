<template>
    <client-only>
        <div class="page-wrapper">
            <Menu />
            <div class="content-wrapper">
                <slot />
                <ActiveTasks class="active-tasks"></ActiveTasks>
            </div>
        </div>
    </client-only>
</template>
<style scoped lang="scss">
.page-wrapper {
    background-color: #f2f0f7;
    width: 100%;
    height: 100%;
    display: flex;
}
.content-wrapper {
    width: 100%;
    margin-bottom: 55px;
}
</style>
<script setup lang="ts">
import ActiveTasks from "~/components/task_history/ActiveTasks.vue";

</script>
<style lang="scss" scoped>
.active-tasks {
    position: fixed;
    bottom: 0;
    right: 0;
    margin-right: 16px;
    margin-bottom: 16px;
    width: 330px;
    background-color: #f2f0f7;
    border-radius: 4px;
}
</style>
