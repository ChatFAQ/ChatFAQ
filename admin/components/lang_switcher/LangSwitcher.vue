<template>
    <div class="language-wrapper">
        <el-select v-model="$i18n.locale" @change="changeLang">
            <el-option
                v-for="item in [{value: 'en', label: $t('Language: EN')}, {value: 'es', label: $t('Lengua: ES')}, {value: 'fr', label: $t('Langue: FR')}]"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
            <template v-slot:prefix>
                <el-icon>
                    <ArrowDown/>
                </el-icon>
            </template>
        </el-select>
    </div>
</template>

<script setup>
import {ArrowDown} from "@element-plus/icons-vue";
import {useLangStore} from "~/store/lang.js";
import {useI18n} from "vue-i18n";

const langStore = useLangStore();
if (!process.server) {
    const i18n = useI18n()
    i18n.locale.value = langStore.lang;
}

const changeLang = (val) => {
    langStore.setLang(val);
}
</script>

<style lang="scss">
.language-wrapper {
    .el-select {
        padding: 0px 24px 0px 24px;
    }
    .el-input__wrapper {
        background-color: transparent;
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
        .el-input__inner {
            color: white !important;
            font-family: Open Sans;
            font-size: 14px;
            font-weight: 400;
            line-height: 20px;
            margin-left: 8px
        }
    }
    svg {
        color: white;
    }
    .el-input__suffix-inner {
        display: none;
    }
}
</style>
