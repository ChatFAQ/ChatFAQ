<template>
    <MenuItem v-if="store.downloading">
        <i class="download-icon"/>
        <span>{{ $t("confirm") }}</span>
        <div class="confirm-controls">
            <i class="close-icon" @click="() => {store.downloading = false}"/>
            <i class="check-icon" @click="downloadHistory"/>
        </div>
    </MenuItem>
    <MenuItem v-else @click="store.downloading = true; store.deleting = false;">
        <i class="download-icon"/>
        <span v-if="store.selectedConversations.length">{{ $t("downloadselected") }}</span>
        <span v-else>{{ $t("downloadhistory") }}</span>
    </MenuItem>
</template>

<script setup>

import { useGlobalStore } from "~/store";

const store = useGlobalStore()

async function downloadHistory() {
    let filename = '';
    const ids = store.selectedConversations.length ? store.selectedConversations : store.conversationsIds
    fetch(
        store.chatfaqAPI + `/back/api/broker/conversations/${ids}/download/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        }
    ).then(res => {
        const header = res.headers.get('Content-Disposition');
        const parts = header.split(';');
        filename = parts[1].split('=')[1].replaceAll("\"", "");
        store.downloading = false
        return res.blob()
    }).then(blob => {
        var a = document.createElement("a");
        a.href = window.URL.createObjectURL(blob);
        a.download = filename;
        a.click();
    });
}

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
</script>


<style lang="scss" scoped>

.download-icon {
    content: $chatfaq-download-icon;
}
.close-icon {
    content: $chatfaq-close-icon;
}
.check-icon {
    content: $chatfaq-check-icon;
}
.confirm-controls {
    width: 100%;
    display: flex;
    flex-direction: row-reverse;
}
</style>

