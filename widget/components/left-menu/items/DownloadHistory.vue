<template>
    <MenuItem @click="downloadHistory">
        <i class="download-icon"/>
        <span>{{ $t("downloadhistory") }}</span>
    </MenuItem>
</template>

<script setup>

import { useGlobalStore } from "~/store";

const store = useGlobalStore()

async function downloadHistory() {
    let filename = '';
    fetch(
        store.chatfaqAPI + `/back/api/broker/conversations-download`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                ids: store.selectedConversations.length ? store.selectedConversations : store.conversationsIds
            })
        }
    ).then(res => {
        const header = res.headers.get('Content-Disposition');
        const parts = header.split(';');
        filename = parts[1].split('=')[1].replaceAll("\"", "");
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
@import "assets/styles/variables";

.download-icon {
    content: $chatfaq-download-icon;
}
</style>

