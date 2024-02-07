import {defineStore} from 'pinia';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: !!useCookie('token').value
    }),
    actions: {
        async login({email, password, remember}) {
            const {data} = await useFetch('/back/api/login/', {
                method: 'post',
                headers: {
                    'Authorization': `Basic ${btoa(email + ":" + password)}`
                },
                body: {
                    rememberme: remember
                },
            });
            if (data.value) {
                let token
                token = useCookie('token');
                token.value = data?.value?.token;
                this.isAuthenticated = true;
            }
        },
        logout() {
            useCookie('token').value = null;
            this.isAuthenticated = false;
        },
    }
});
