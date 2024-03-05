<template>
    <div class="login-wrapper">
        <div class="chatfaq-logo-wrapper">
            <div class="chatfaq-logo"></div>
        </div>
        <h1 class="login-title">{{ $t("welcometochatfaq") }}</h1>
        <h2 class="login-subtitle">{{ $t("pleaseenteryourdetails") }}</h2>
        <el-form
            class="login-form"
            ref="authFormRef"
            :model="authForm"
            :rules="authFormRules"
            status-icon
            label-position="top"
            require-asterisk-position="right"
            @keydown.enter.native="submitForm(authFormRef)"
        >
            <el-form-item :label="$t('email')" prop="email">
                <el-input v-model="authForm.email" :placeholder="$t('enteryouremail')"/>
            </el-form-item>
            <el-form-item class="login-form-password" :label="$t('password')" prop="password">
                <el-input v-model="authForm.password" :placeholder="$t('enteryourpassword')" type="password"
                          autocomplete="off" show-password  :validate-event="false"/>
            </el-form-item>
            <client-only>
                <el-form-item prop="remember" class="login-form-remember-me">
                    <el-checkbox v-model="authForm.remember" :label="$t('rememberme')"/>
                    <span class="login-form-forgot-password" @click="openPassNotification">Forgot password?</span>
                </el-form-item>
            </client-only>
            <el-form-item>
                <el-button type="primary" @click="submitForm(authFormRef)">
                    {{ $t('login') }}
                </el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
definePageMeta({
  layout: 'empty'
})

</script>
<script setup>
import {reactive, ref} from 'vue'
import {useAuthStore} from '~/store/auth';
import {useI18n} from "vue-i18n";
import { ElMessage } from "element-plus";

const i18n = useI18n()
const authStore = useAuthStore()
const router = useRouter()
const authFormRef = ref()
let email = ""
let password = ""
let remember = false
let serverError = false

if (process.client) {
    let rememberMeCookie = document.cookie.split(';').filter((item) => item.trim().startsWith('rememberme='))
    if (rememberMeCookie.length > 0) {
        rememberMeCookie = rememberMeCookie[0].split('=')[1]
        email = rememberMeCookie.split("-").slice(5, rememberMeCookie.split("-").length).join("-")
        email = decodeURIComponent(email)
        password = "**********"
        remember = true
    }
}
const authForm = reactive({
    email: email,
    password: password,
    remember: remember,
})
const serverErrorValidator = (rule, value, callback) => {
    if (serverError) {
        return callback(i18n.t('invalidemailorpassword'))
    }
    callback()
}
const authFormRules = reactive({
    email: [
        {required: true, message: i18n.t('pleaseenteryouemailaddress'), trigger: 'blur'},
        {type: 'email', message: i18n.t('pleaseenteravalidemailaddress'), trigger: 'blur'},
    ],
    password: [
        {required: true, message: i18n.t('pleaseenteryourpassword'), trigger: 'blur'},
        {validator: serverErrorValidator, trigger: 'blur'}
    ],
    remember: [],
})
const submitForm = async (formEl) => {
    serverError = false
    if (!formEl) return
    await formEl.validate(async (valid, fields) => {
        if (valid) {
            await authStore.login(authForm);
            if (authStore.isAuthenticated) {
                router.push('/');
            } else {
                serverError = true
                formEl.validate()
            }
        } else {
            console.log('error submit!', fields)
        }
    })
}
function openPassNotification() {
    ElMessage.info(i18n.t('contactadmin'));
}
</script>
<style lang="scss">
.login-wrapper {
    .el-form-item__label::after {
        display: none;
    }
}
</style>
<style lang="scss" scoped>
@import "assets/styles/variables";

.login-wrapper {
    width: 330px;

    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);

    .chatfaq-logo-wrapper {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-bottom: 60px;

        .chatfaq-logo {
            content: url("~/assets/images/logo.svg");
        }
    }

    .login-title {
        font-family: "Montserrat";
        font-size: 24px;
        font-weight: 700;
        line-height: 30px;
        letter-spacing: 0em;
        text-align: left;
        margin: 0px;
    }

    .login-subtitle {
        font-size: 14px;
        font-weight: 400;
        line-height: 20px;
        letter-spacing: 0em;
        text-align: left;
        margin-top: 8px;
    }

    .login-form {
        margin-top: 32px;

        .login-form-password {
            margin-top: 32px;
            margin-bottom: 16px;
        }
    }
}
</style>

<style lang="scss">
.login-wrapper {
    .el-form-item__label {
        color: $chatfaq-color-inputLabel-dark;
        font-size: 14px;
        font-weight: 600;
        line-height: 20px;
        letter-spacing: 0em;
        text-align: left;

    }

    .el-input__wrapper {
        width: 328px;
        height: 40px;
        padding: 9px 11px 11px 16px;
        border-radius: 10px;
        border: 1px;
        gap: 10px;

        ::placeholder {
            color: #80858d;
            opacity: 1;
        }
    }

    .el-checkbox {
        height: unset;
        line-height: unset;

        .el-checkbox__label {
            color: #80858d;
        }

        &.is-checked {
            .el-checkbox__label {
                color: $chatfaq-color-inputLabel-dark;
            }
            .el-checkbox__inner {
                background-color: $chatfaq-color-inputLabel-dark;
                border-color: $chatfaq-color-inputLabel-dark;
            }
        }
    }

    .login-form-remember-me {

        .el-form-item__content {
            justify-content: space-between;
            height: unset;
            line-height: unset;
        }

        .login-form-forgot-password {
            color: $chatfaq-color-forgot-pass-text-dark;
            text-decoration: underline;
            cursor: pointer;
        }
    }

    .el-button {
        width: 100%;
        height: 36px;
        padding: 8px 32px 8px 32px;
        border-radius: 8px;
        gap: 10px;
        background-color: $chatfaq-color-button-dark;
        border: none;
        margin-top: 32px;
    }
}
</style>
