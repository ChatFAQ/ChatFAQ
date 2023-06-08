<template>
    <div class="loader-wrapper">
        <div class="loader"></div>
    </div>
</template>


<script setup>

</script>

<style lang="scss" scoped>
@import "assets/styles/variables";

.loader-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    width: calc(3.5em + (2.5em)/2);
}
.loader, .loader:before, .loader:after {
    border-radius: 50%;
    width: 2.5em;
    height: 2.5em;
    animation: bblFadInOut 1.8s infinite ease-in-out;
}

.loader {
    color: #FFF;
    font-size: 7px;
    transform: translateZ(0);
    animation-delay: -0.16s;
}

.loader:before,
.loader:after {
    content: '';
    position: absolute;
}

.loader:before {
    left: -3.5em;
    animation-delay: -0.32s;
}

.loader:after {
    left: 3.5em;
}

@keyframes bblFadInOut {
    0%, 80%, 100% {
        box-shadow: 0 2.5em 0 -1.3em
    }
    40% {
        box-shadow: 0 2.5em 0 0
    }
}

</style>


