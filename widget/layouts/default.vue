<template>
    <slot/>
</template>
<script>
export default {
    head() {
        return {
            bodyAttrs: {
                class: 'reset-body'
            }
        }
    }
}
</script>

<style>
.reset-body {
    margin: 0
}
</style>
