<template>
    <div class="menu-item">
        <slot></slot>
    </div>
</template>

<script setup>
</script>


<style lang="scss">

.menu-item {
    display: flex;
    align-items: center;
    padding: 8px 8px;
    margin: 4px 0px;
    letter-spacing: 0.5px;
    border-radius: 4px;
    *:first-child {
        margin-right: 8px;
        svg {
            margin-right: 8px;
        }
    }
    &:hover {
        background-color: $chatfaq-color-menuItem-background-hover;
    }
}
</style>

