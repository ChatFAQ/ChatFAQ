<template>
<div class="stat-card-wrapper">
    <div class="stat-title">{{title}}</div>
    <div class="stat-content">{{content}}</div>
</div>
</template>

<script setup>

import { ref, watch, defineProps } from 'vue'

// attribute props
const props = defineProps({
    title: {
        type: String,
        required: true
    },
    content: {
        type: String,
        required: true
    }
});

</script>


<style lang="scss" scoped>
.stat-card-wrapper {
    height: 106px;
    padding: 24px;
    border-radius: 10px;
    border: 1px;
    gap: 24px;
    border: 1px solid #DFDAEA;
    background: #FFFFFF99;
    .stat-title {
        font-family: Open Sans;
        font-size: 14px;
        font-weight: 400;
        line-height: 20px;
        letter-spacing: 0em;
        text-align: left;
        color: #020C1C;
        margin-bottom: 8px;
    }
    .stat-content {
        //styleName: Title/SM/Bold;
        font-family: Montserrat;
        font-size: 24px;
        font-weight: 700;
        line-height: 30px;
        letter-spacing: 0em;
        text-align: left;
        color: #020C1C;
    }
}
</style>
