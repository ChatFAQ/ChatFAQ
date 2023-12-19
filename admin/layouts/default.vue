<template>
    <div class="page-wrapper">
        <Menu />
        <div class="content-wrapper">
            <slot />
            <ActiveTasks class="active-tasks"></ActiveTasks>
        </div>
    </div>
</template>
<style scoped lang="scss">
.page-wrapper {
    background-color: #f2f0f7;
    width: 100%;
    height: 100%;
    display: flex;
}
.content-wrapper {
    margin-top: 25px;
    margin-left: 40px;
    width: 100%;
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
    margin-right: 40px;
    margin-bottom: 40px;
    width: 330px;
    background-color: #f2f0f7;
    border-radius: 4px;
}
</style>
