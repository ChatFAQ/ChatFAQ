<template>
    <div class="dashboard-page-title">{{ $t('widgetconfig') }}</div>
    <el-tabs class="main-page-tabs" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('widget')" name="widgetsettings">
            <ReadWriteView
                ref="readWriteViewWidget"
                :readableName="$t('widget')"
                apiUrl="/back/api/widget/widgets/"
                :cardProps="{
                'domain': $t('domain'),
                'fsm_def': $t('fsmdef'),
                }"
                :tableProps="{
                'name': {'name': $t('name')},
                'domain': {'name': $t('domain')},
                'fsm_def': {'name': $t('fsmdef')},
                }"
                @submitFormStart="submitMessageLayout"
                @initializedFormValues="initializedFormValues"
                :sections="{
                [$t('general')]: [
                        'name',
                        'domain',
                        'fsm_def',
                    ],
                [$t('layout')]: [
                        'maximized',
                        'fullScreen',
                        'history_opened',
                        'title',
                        'subtitle',
                        'manage_user_id',
                    ],
                [$t('messagelayout')]: [
                        'messagelayout'
                    ],
                [$t('theme')]: [
                        'theme'
                    ],
                [$t('script')]: [
                        'script',
                    ]
                }"
            >
                <template v-slot:write-script="props">
                    <ExampleScript :editing="readWriteViewWidget.editing"/>
                </template>
                <template v-slot:write-messagelayout="{schema, form}">
                    <div>
                        <el-form-item :label="$t('elementsshown') + ' *'">
                            <el-radio v-model="elementsShown" label="tt">{{ $t('both') }}</el-radio>
                            <el-radio v-model="elementsShown" label="tf">{{ $t('generation') }}</el-radio>
                            <el-radio v-model="elementsShown" label="ft">{{ $t('sources') }}</el-radio>
                        </el-form-item>
                        <el-form-item :label="$t('displayorder') + ' *'">
                            <el-select v-model="displayingOrder" placeholder="Select" style="width: 240px">
                                <el-option
                                    v-for="item in displayingOrderOptions"
                                    :key="item.value"
                                    :label="item.label"
                                    :value="item.value"
                                />
                            </el-select>
                        </el-form-item>
                    </div>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('theme')" name="theme">
            <ReadWriteView
                :readableName="$t('theme')"
                apiUrl="/back/api/widget/themes/"
                :cardProps="{
                }"
                :tableProps="{
                    'name': {'name': $t('name')},
                }"
                :outsideSection="['data']"
                @submitFormStart="submitFieldData"
            >
                <template v-slot:write-data="props">
                    <FieldData :form="props.form" :fieldName="props.fieldName" ref="fieldData">123</FieldData>
                </template>
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import {useItemsStore} from "~/store/items.js";
import FieldData from "~/components/widget_config/fields/FieldData.vue";
import ExampleScript from "~/components/widget_config/fields/ExampleScript.vue";
import {useI18n} from "vue-i18n";

const { t } = useI18n();

const fieldData = ref(null)
const readWriteViewWidget = ref({})

const {$axios} = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("widgetsettings")
const elementsShown = ref('tt')
const displayingOrder = ref(true)
const displayingOrderOptions = ref([{
    value: false,
    label: t('generationfirst'),
}, {
    value: true,
    label: t('sourcesfirst'),
}])
await itemsStore.loadSchema()

function submitFieldData() {
    fieldData.value.submit()
}
function initializedFormValues(form) {
    displayingOrder.value = form.sources_first
    elementsShown.value = form.display_generation.toString()[0] + form.display_sources.toString()[0]
}
function submitMessageLayout(_, form) {
    form.display_generation = elementsShown.value[0] === 't'
    form.display_sources = elementsShown.value[1] === 't'
    form.sources_first = displayingOrder.value
}
</script>
