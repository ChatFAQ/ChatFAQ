<template>
    <div class="back-button">
        <el-icon>
            <ArrowLeft/>
        </el-icon>
        <slot>
            <span>{{ $t("back") }}</span>
        </slot>
    </div>
</template>

<script setup>
</script>
<style lang="scss" scoped>
.back-button {
    display: flex;
    cursor: pointer;
    align-items: center;
    font-size: 12px;
    font-weight: 600;
    color: $chatfaq-color-primary-500;

    i {
        margin-right: 8px;
    }
}
</style>
