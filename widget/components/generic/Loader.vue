<template>
    <div class="custom-loader" :class="{ dark: color }"></div>
</template>


<script setup>
defineProps({
    color: {
        type: Boolean,
        default: false,
    }
})
</script>

<style lang="scss" scoped>

.custom-loader {
    width: 50px;
    height: 9px;
    $color: $chatfaq-color-loader-light;
    background: radial-gradient(circle closest-side,  $color 90%, #0000) 0% 50%,
    radial-gradient(circle closest-side,  $color 90%, #0000) 50% 50%,
    radial-gradient(circle closest-side,  $color 90%, #0000) 100% 50%;
    background-size: calc(100% / 3) 100%;
    background-repeat: no-repeat;
    animation: d7 1s infinite linear;

    &.dark {
        $color: $chatfaq-color-loader-dark;
        background: radial-gradient(circle closest-side,  $color 90%, #0000) 0% 50%,
        radial-gradient(circle closest-side,  $color 90%, #0000) 50% 50%,
        radial-gradient(circle closest-side,  $color 90%, #0000) 100% 50%;
    }
}

@keyframes d7 {
    33% {
        background-size: calc(100% / 3) 0%, calc(100% / 3) 100%, calc(100% / 3) 100%
    }
    50% {
        background-size: calc(100% / 3) 100%, calc(100% / 3) 0%, calc(100% / 3) 100%
    }
    66% {
        background-size: calc(100% / 3) 100%, calc(100% / 3) 100%, calc(100% / 3) 0%
    }
}

</style>


