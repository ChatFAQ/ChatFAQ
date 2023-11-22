<template>
    <div class="chatfaq-demo">
        <div class="chatfaq-logo">
            <div class="chatfaq-cq-icon"></div>
            <div class="chatfaq-icon"></div>
        </div>
        <MenuItem icon="House" :name="$t('dashboard')" page="/dashboard"/>
        <MenuItem icon="Edit" :name="$t('labeling')" page="/labeling"/>
        <MenuItem icon="Reading" :name="$t('data')" page="/data"/>
        <MenuItem icon="SetUp" :name="$t('aiconfig')" page="/ai_config/"/>
        <MenuItem icon="Brush" :name="$t('widgetconfig')" page="/widget_config"/>
        <MenuItem icon="DataBoard" :name="$t('sdkvisualizer')" page="/sdk_visualizer"/>
        <MenuItem icon="TrendCharts" :name="$t('stats')" page="/stats"/>
        <MenuItem icon="User" :name="$t('usermanagement')" page="/user_management"/>
        <MenuItem icon="Clock" :name="$t('taskhistory')" page="/task_history"/>
        <div class="separator"></div>
        <MenuItem icon="Setting" :name="$t('accountsettings')" page="account_settings"/>

        <div class="menu-bottom">
            <div class="separator"></div>
            <MenuItem @click="logOut" icon="SwitchButton" :name="$t('logout')"/>
        </div>
    </div>
</template>
<script setup>
import { useAuthStore } from '~/store/auth';

const authStore = useAuthStore();
const router = useRouter();

function logOut() {
    authStore.logout();
    router.push('/login');
}
</script>
<style lang="scss" scoped>
.chatfaq-demo {
    background-color: $chatfaq-color-primary-900;
    padding-top: 10px;
    padding-bottom: 10px;
    height: 100dvh;
    width: 240px;
    display: flex;
    flex-flow: column;
}

.chatfaq-logo {
    width: 100%;
    display: flex;
    padding: 12px 24px 12px 24px;

    .chatfaq-cq-icon {
        background-image: url('~/assets/icons/chatfaq-cq-icon.svg');
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 2px;
    }

    .chatfaq-icon {
        background-image: url('~/assets/icons/chatfaq-icon.svg');
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
        width: 100%;
        height: 15px;
    }

}

.separator {
    height: 1px;
    background-color: $chatfaq-color-neutral-purple;
    margin-top: 16px;
    margin-bottom: 16px;
}

.menu-bottom {
    width: 240px;
    display: flex;
    justify-content: flex-end;
    flex-flow: column;
    height: 100%;
}
</style>
