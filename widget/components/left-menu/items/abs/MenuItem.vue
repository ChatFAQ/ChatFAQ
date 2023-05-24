<template>
    <div class="menu-item">
        <slot></slot>
    </div>
</template>

<script setup>
</script>


<style lang="scss">
@import "assets/styles/variables";

.menu-item {
    display: flex;
    padding: 12px 12px;
    letter-spacing: 0.5px;
    border-radius: 4px;
    i {
        margin-right: 10px;
    }
}
</style>

