<template>
    <div class="page-wrapper">
        <Menu/>
        <div>
            <slot/>
        </div>
    </div>
</template>

<style scoped lang="scss">
.page-wrapper {
    background-color: green;
    width: 100vw;
    height: 100vh;
    display: flex;
}
</style>
