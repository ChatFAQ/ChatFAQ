import {useAuthStore} from "~/store/auth.js";

export default defineNuxtRouteMiddleware((to) => {
    const authStore = useAuthStore();
    if (authStore.isAuthenticated && to?.name === 'login') {
        abortNavigation();
        return navigateTo('/');
    }

    if (!authStore.isAuthenticated && to?.name !== 'login') {
        abortNavigation();
        return navigateTo('/login');
    }
});
