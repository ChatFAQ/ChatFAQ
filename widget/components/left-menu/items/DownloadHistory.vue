<template>
    <MenuItem v-if="store.downloading">
        <Download class="download-icon"/>
        <span>{{ $t("confirm") }}</span>
        <div class="confirm-controls">
            <Close class="close-icon" @click="() => {store.downloading = false}"/>
            <Check class="check-icon" @click="downloadHistory"/>
        </div>
    </MenuItem>
    <MenuItem v-else @click="store.downloading = true; store.deleting = false;">
        <Download class="download-icon"/>
        <span v-if="store.selectedConversations.length">{{ $t("downloadselected") }}</span>
        <span v-else>{{ $t("downloadhistory") }}</span>
    </MenuItem>
</template>

<script setup>

import Check from "~/components/icons/Check.vue";
import Close from "~/components/icons/Close.vue";

import { useGlobalStore } from "~/store";

const store = useGlobalStore()

async function downloadHistory() {
    if (store.previewMode)
        return
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
import Download from "~/components/icons/Download.vue";
</script>


<style lang="scss" scoped>

.download-icon {
    color: $chatfaq-download-icon-color;
}

.confirm-controls {
    margin-left: auto;
    display: flex;
    flex-direction: row-reverse;
    .check-icon {
        color: $chatfaq-check-icon-color;
    }
    .close-icon {
        color: $chatfaq-close-icon-color;
    }
}
</style>

