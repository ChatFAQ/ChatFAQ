<template>
    <div class="page-wrapper">
        <Menu />
        <div>
            <slot />
        </div>
    </div>
</template>

<style scoped lang="scss">
.page-wrapper {
    background-color: #f2f0f7;
    width: 100vw;
    height: 100vh;
    display: flex;
}
</style>
