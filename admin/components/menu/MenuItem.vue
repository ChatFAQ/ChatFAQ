<template>
    <div class="chatfaq-menu-item" :class="{selected: router.currentRoute.value.path == page }" @click="goToPage">
        <el-icon class="icon">
            <Component :is="iconComponent" />
        </el-icon>
        <div class="name">{{ name }}</div>
    </div>
</template>
<script setup>
import { defineProps } from 'vue';
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const router = useRouter();
const props = defineProps({
    icon: {
        type: String,
        mandatory: true
    },
    name: {
        type: String,
        mandatory: true
    },
    page: {
        type: String,
        mandatory: false
    }
})

const iconComponent = shallowRef(resolveComponent(props.icon))

function goToPage() {
    if (props.page) {
        itemsStore.stateToRead()
        router.push(props.page)
    }
}

</script>
<style lang="scss">
.chatfaq-menu-item {
    display: flex;
    color: white;
    padding: 12px 24px 12px 24px;
    align-items: center;
    &:hover, &.selected {
        background-color: $chatfaq-color-primary-500;
    }
    .icon {
        margin-right: 8px;
    }
    &:hover {
        cursor: pointer;
    }


}
</style>
