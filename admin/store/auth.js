import {defineStore} from 'pinia';
import {authHeaders} from "~/store/items.js";

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: !!useCookie('token').value,
        userName: undefined
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
            this.userName = undefined;
        },
        async getUserName() {
            if (!this.isAuthenticated) {
                return undefined;
            }
            if (!this.userName) {
                const {$axios} = useNuxtApp();
                const res = await $axios.get('/back/api/people/people/', {'headers': authHeaders()});
                this.userName = res.data.first_name;
            }
            return this.userName;
        }
    },
});
