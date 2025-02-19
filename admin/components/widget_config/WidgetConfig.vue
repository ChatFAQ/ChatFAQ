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
                :sections="{
                [$t('general')]: [
                        'name',
                        'domain',
                        'fsm_def',
                        'chatfaq_ws',
                        'lang'
                    ],
                [$t('look & feel')]: [
                        'title',
                        'subtitle',
                        'full_screen',
                        'only_chat',
                        'start_small_mode',
                        'start_with_history_closed',
                        'disable_day_night_mode',
                        'enable_logout',
                        'hide_sources',
                        'sources_first',
                        'stick_input_prompt',
                        'fit_to_parent',
                        'stick_input_prompt',
                        'allow_attachments',
                    ],
                [$t('interfacing')]: [
                        'speech_recognition',
                        'speech_recognition_lang',
                        'speech_recognition_auto_send',
                        'speech_recognition_always_on',
                        'speech_recognition_phrase_activation',
                        'speech_synthesis',
                        'speech_synthesis_pitch',
                        'speech_synthesis_rate',
                        'speech_synthesis_voices',
                        'speech_synthesis_enabled_by_default'
                    ],
                [$t('advanced')]: [
                        'custom_css',
                        'initial_conversation_metadata',
                        'custom_i_framed_msgs',
                        'enable_resend',
                    ],
                [$t('theme')]: [
                        'theme'
                    ],
                [$t('authentication')]: [
                        'authentication_required'
                    ],
                [$t('script')]: [
                        'script',
                    ]
                }"
            >
                <template v-slot:write-script="props">
                    <ExampleScript :editing="readWriteViewWidget.editing"/>
                </template>

                <template v-slot:write-custom_i_framed_msgs="{fieldName, form, formServerErrors}">
                    <el-form-item :label="$t(fieldName)"
                                  :prop="fieldName"
                                  :error="formServerErrors[fieldName]">
                        <el-input
                            class="prompt-input"
                            v-model="form[fieldName]"
                            autosize
                            @keydown.enter.stop
                            type="textarea"
                        />
                    </el-form-item>
                </template>
                <template v-slot:write-initial_conversation_metadata="{fieldName, form, formServerErrors}">
                    <el-form-item :label="$t(fieldName)"
                                  :prop="fieldName"
                                  :error="formServerErrors[fieldName]">
                        <el-input
                            class="prompt-input"
                            v-model="form[fieldName]"
                            autosize
                            @keydown.enter.stop
                            type="textarea"
                        />
                    </el-form-item>
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
                contentType="application/json"
                @submitFormStart="submitFieldData"
            >
                <template v-slot:write-data="props">
                    <FieldData @css-change="updatePreview" :form="props.form" :fieldName="props.fieldName" ref="fieldData"/>
                </template>

                <template v-slot:bottom-write>
                    <teleport to=".active-tasks-wrapper">
                        <chatfaq-widget
                            :data-title="title"
                            :data-subtitle="subtitle"
                            data-preview-mode
                            data-start-small-mode
                            data-speech-recognition
                            allow-attachments
                        ></chatfaq-widget>
                    </teleport>
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
const conf = useRuntimeConfig()

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
const customCss = ref("")
await itemsStore.loadSchema()

function submitFieldData() {
    fieldData.value.submit()
}

function getCss(formObj) {
    let css = ":root {";
    for (let cssVar in formObj) {
        let value = formObj[cssVar];
        if (typeof value === 'object') {
            css += `--${cssVar}-light: ${value.light};`;
            css += `--${cssVar}-dark: ${value.dark};`;
        } else {
            css += `--${cssVar}: ${value};`;
        }
    }
    css += "}";

    return css;
}

function updatePreview() {
    if(!fieldData.value)
        return
    fieldData.value.submit()
    const p = fieldData.value.props
    customCss.value = getCss(p.form[p.fieldName])

    const cssElement = document.getElementById("custom-css");
    if (cssElement)
        cssElement.remove();
    const style = document.createElement('style');
    style.id = "custom-css";
    style.innerHTML = customCss.value;
    document.head.appendChild(style);
}

const title = ref("Hello there 👋")
const subtitle = ref("How can we help you?")
</script>

<style >
.chatfaq-widget {
    display: block !important;
    position: relative !important;
}
</style>
