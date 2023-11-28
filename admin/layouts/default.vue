<template>
    <div class="page-wrapper">
        <Menu />
        <div class="content-wrapper">
            <slot />
        </div>
    </div>
</template>

<style scoped lang="scss">
.page-wrapper {
    background-color: #f2f0f7;
    width: 100%;
    height: 100%;
    display: flex;
}
.content-wrapper {
    margin-top: 25px;
    margin-left: 40px;
    width: 100%;
}
</style>
