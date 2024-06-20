<template>
    <client-only>
        <Suspense>
            <template #default>
                <UserManagement/>
            </template>
            <template #fallback>
                <div class="main-component-page-loader" v-loading="true" />
            </template>
        </Suspense>
    </client-only>
</template>

<script setup>
import UserManagement from "~/components/user_management/UserManagement.vue";
</script>
