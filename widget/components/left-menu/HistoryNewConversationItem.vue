<template>
    <div class="history-item">
        <i class="plus"/> {{ $t("newconversation") }}
    </div>
</template>

<script setup>

</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.history-item {
    padding: 8px 8px 8px 8px;

    color: $chatfaq-color-neutral-white;

    letter-spacing: 0.5px;
    i {
        margin-right: 5px;
    }
    .plus {
        content: $chatfaq-plus;
    }
}
</style>

