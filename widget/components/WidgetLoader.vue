<template>
    <div v-if="opened" class="widget-wrapper">
        <div class="widget-wrapper-header" @click="opened = false"></div>
        <Widget class="widget"/>
    </div>
    <div v-else class="widget-open-button" @click="opened = true"></div>
</template>

<script setup>
const selectedFSMDef = useState("selectedFSMDef")
const opened = ref()
</script>

<style lang="scss" scoped>
    .widget-wrapper {
        border: solid 1px;
        border-radius: 5px;
        border-color: #FF8E93;
        width: 300px;
        height: 450px;
        position: absolute;
        display: flex;
        align-items: stretch;
        flex-flow: column;
        bottom: 0px;
        right: 0px;
        margin: 25px;
    }
    .widget-wrapper-header {
        cursor: pointer;
        background-color: #FF8E93;
        height: 50px;
    }
    .widget-wrapper > .widget {
        position: relative;
        height: 100%;
    }
    .widget-open-button {
        cursor: pointer;
        background-color: #FF8E93;
        width: 50px;
        height: 50px;
        border-radius: 50px;
        position: absolute;
        bottom: 0px;
        right: 0px;
        margin: 25px;
    }
</style>

