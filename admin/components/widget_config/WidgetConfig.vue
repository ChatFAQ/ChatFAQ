<template>
    <div class="dashboard-page-title">{{ $t('usermanagement') }}</div>
    <el-tabs @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('widgetsettings')" name="widgetsettings">
            <ReadWriteView readableName="Widget settings" apiUrl="/back/api/widget/widgets/"
                           titleProp="name"
                           :cardProps="{
                'name': $t('name'),
                'domain': $t('domain'),
                'fsm_name': $t('fsmname'),
                }"
                           :tableProps="{
                'name': $t('name'),
                'domain': $t('domain'),
                'fsm_name': $t('fsmname'),
                }"
                           :sections="{
                [$t('script')]: [
                        'script',
                    ],
                [$t('general')]: [
                        'name',
                        'domain',
                        'fsm_name',
                    ],
                [$t('layout')]: [
                        'size',
                        'history_opened',
                        'title',
                        'subtitle',
                    ],
                [$t('theme')]: [
                        'theme'
                    ]
                }"
            >
                <template v-slot:script="props">
                    <div :form="props.form" :fieldName="props.fieldName">123</div>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('theme')" name="theme">
            <ReadWriteView
                readableName="theme"
                apiUrl="/back/api/widget/themes/"
                :cardProps="{
                    'name': $t('name'),
                }"
                :tableProps="{
                    'name': $t('name'),
                }"
                :outsideSection="['data']"
                @submitForm="submitFieldData"
            >
                <template v-slot:data="props">
                    <FieldData :form="props.form" :fieldName="props.fieldName"  ref="fieldData">123</FieldData>
                </template>
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import { useItemsStore } from "~/store/items.js";
import Password from "~/components/user_management/fields/Password.vue";
import FieldData from "~/components/widget_config/fields/FieldData.vue";

const fieldData = ref(null)

const { $axios } = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("widgetsettings")
await itemsStore.loadSchema($axios)

function submitFieldData() {
    fieldData.value.submit()
}
</script>
