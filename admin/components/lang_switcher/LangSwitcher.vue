<template>
    <div class="language-wrapper">
        <el-select v-model="$i18n.locale">
            <el-option
                v-for="item in [{value: 'en', label: $t('Language: EN')}, {value: 'es', label: $t('Lengua: ES')}, {value: 'fr', label: $t('Langue: FR')}]"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
        </el-select>
    </div>
</template>

<script setup>
</script>

<style lang="scss">
.language-wrapper {
    .el-input__wrapper, .el-select {
        display: flex;
        flex-direction: row-reverse;
        background-color: transparent;
        box-shadow: none !important;
        border: none !important;

        .el-input__inner {
            color: white !important;
            font-family: Open Sans;
            font-size: 14px;
            font-weight: 400;
            line-height: 20px;
            margin-left: 8px
        }
    }
}
</style>
