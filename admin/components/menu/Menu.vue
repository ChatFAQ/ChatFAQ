<template>
    <div class="chatfaq-demo">
        <div class="chatfaq-logo">
            <div class="chatfaq-cq-icon"></div>
            <div class="chatfaq-icon"></div>
        </div>
        <MenuItem icon="House" name="Dashboard" page="dashboard"/>
        <MenuItem icon="Edit" name="Labeling" page="labeling"/>
        <MenuItem icon="Reading" name="Data" page="data"/>
        <MenuItem icon="SetUp" name="AI Config" page="ai_config"/>
        <MenuItem icon="Brush" name="Widget Config" page="widget_config"/>
        <MenuItem icon="DataBoard" name="SDK Visualizer" page="sdk_visualizer"/>
        <MenuItem icon="TrendCharts" name="Stats" page="stats"/>
        <MenuItem icon="User" name="User Management" page="user_management"/>
        <MenuItem icon="Clock" name="Task history" page="task_history"/>
        <div class="separator"></div>
        <MenuItem icon="Setting" name="Account settings" page="account_settings"/>

        <div class="menu-bottom">
            <div class="separator"></div>
            <MenuItem @click="logOut" icon="SwitchButton" name="Log Out"/>
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
<style lang="scss">
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
