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
            });
            if (data.value) {
                let token
                if (remember) {
                    token = useCookie('token', {
                        maxAge: 365 * 24 * 60 * 60,  // 1 year
                    });
                } else {
                    token = useCookie('token');
                }
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
