<template>
    <div class="custom-loader"></div>
</template>


<script setup>
defineProps({
    color: {
        type: String,
        default: "white"
    }
})
</script>

<style lang="scss" scoped>
@import "assets/styles/variables";

.custom-loader {
    width: 50px;
    height: 9px;
    background: radial-gradient(circle closest-side,  v-bind(color) 90%, #0000) 0% 50%,
    radial-gradient(circle closest-side,  v-bind(color) 90%, #0000) 50% 50%,
    radial-gradient(circle closest-side,  v-bind(color) 90%, #0000) 100% 50%;
    background-size: calc(100% / 3) 100%;
    background-repeat: no-repeat;
    animation: d7 1s infinite linear;
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


