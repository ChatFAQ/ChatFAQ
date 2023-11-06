<template>
    <div>Hello Home Page</div>
    <el-button @click="logOut">Log Out</el-button>
</template>

<script setup>
import {useAuthStore} from '~/store/auth';

const authStore = useAuthStore();
const router = useRouter();
function logOut() {
    authStore.logout();
    router.push('/login');
}

</script>

