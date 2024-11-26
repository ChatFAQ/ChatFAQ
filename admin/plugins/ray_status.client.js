export default defineNuxtPlugin(async (nuxtApp) => {
    const token = useCookie('token').value
    const options = {
        headers: {
            'Authorization': `Token ${token}`,
        }
    };
    try {
        const response = await $fetch('/back/api/language-model/ray-status/', options)
        const { use_ray } = response
        nuxtApp.provide('useRay', use_ray)
        console.log('Ray status:', use_ray)
    } catch (error) {
        console.warn('Failed to fetch Ray status:', error)
        nuxtApp.provide('useRay', false)
    }
})