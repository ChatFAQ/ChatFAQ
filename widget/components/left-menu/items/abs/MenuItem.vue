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
    padding: 12px 8px;
    letter-spacing: 0.5px;
    i {
        margin-right: 10px;
    }
}
</style>

