import { ElNotification } from "element-plus";
import { authHeaders } from "~/store/items.js";
import { useItemsStore } from "~/store/items.js";
import {useI18n} from "vue-i18n";

export function rgba2hex(orig) {
    if (!orig.toLowerCase().startsWith("rgba"))
        return orig;

    var a, isPercent,
        rgb = orig.replace(/\s/g, "").match(/^rgba?\((\d+),(\d+),(\d+),?([^,\s)]+)?/i),
        alpha = (rgb && rgb[4] || "").trim(),
        hex = rgb ?
            (rgb[1] | 1 << 8).toString(16).slice(1) +
            (rgb[2] | 1 << 8).toString(16).slice(1) +
            (rgb[3] | 1 << 8).toString(16).slice(1) : orig;

    if (alpha !== "") {
        a = alpha;
    } else {
        a = 1;
    }
    // multiply before convert to HEX
    a = ((a * 255) | 1 << 8).toString(16).slice(1);
    hex = hex + a;
    if (hex.endsWith("ff") && hex.length === 8) hex = hex.slice(0, -2);
    return `#${hex}`.toUpperCase();
}

export function formatDate(date) {
    // It receives a date in the format 2024-01-17T15:06:55.931659 and returns 17/01/2024 15:06
    const dateObject = new Date(date);
    let day = dateObject.getDate();
    let month = dateObject.getMonth() + 1;
    let year = dateObject.getFullYear();
    let hour = dateObject.getHours();
    let minutes = dateObject.getMinutes();
    // add ceroes in case of 1 digit to day, month, hour and minutes:
    if (day < 10) day = `0${day}`;
    if (month < 10) month = `0${month}`;
    if (hour < 10) hour = `0${hour}`;
    if (minutes < 10) minutes = `0${minutes}`;

    return `${day}/${month}/${year} ${hour}:${minutes}`;
}

export async function solveRefPropValue(item, propName, itemSchema) {
    const itemsStore = useItemsStore();
    if (!itemSchema)
        return;
    const prop = itemSchema.properties[propName];
    if (!prop) {
        return item[propName];
    }
    if (prop.$ref && itemSchema.properties[propName].choices) {
        // itemSchema.choices has the values for the $ref: [{label: "label", value: "value"}, {...}] item[propName] has the value, we want the label
        let choice;
        if (itemSchema.properties[propName].choices.results)
            choice = itemSchema.properties[propName].choices.results.find(choice => choice.value === item[propName]);
        else
            choice = itemSchema.properties[propName].choices.find(choice => choice.value === item[propName]);
        if (choice)
            return choice.label;
        else if (!choice && prop.$ref) {
            let apiUrl = prop?.choices?.next  // it better ahs a next...
            if (apiUrl) {
                apiUrl = apiUrl.split("?")[0];
                const res = await itemsStore.retrieveItems(apiUrl, {
                    id: item[propName],
                    limit: 0,
                    offset: 0,
                    ordering: undefined
                }, true);
                if (res) {
                    itemSchema.properties[propName].choices.results.push({label: res.name, value: res.id})
                    return res.name
                }
            }
        }
    }
    return item[propName];
}


export async function deleteItem(id, itemsStore, apiUrl, $t) {
    try {
        itemsStore.loading = true;
        await itemsStore.deleteItem(apiUrl, id);
        itemsStore.loading = false;
    } catch (e) {
        itemsStore.loading = false;
        ElNotification({
            title: "Error",
            message: $t("errordeletingitem"),
            type: "error",
            position: "top-right",
        });
        return;
    }
    ElNotification({
        title: "Success",
        message: $t("successdeletingitem"),
        type: "success",
        position: "top-right",
    });
}


export async function callRagReindex(ragId, $t) {
    const {$axios} = useNuxtApp();

    try {
        await $axios.get(`/back/api/language-model/rag-configs/${ragId}/trigger-reindex/`, { "headers": authHeaders() });
    } catch (e) {
        ElNotification({
            title: "Error",
            message: $t("failedtotriggerreindex"),
            type: "error",
            position: "top-right",
        });
        throw e
    }
    ElNotification({
        title: "Success",
        message: $t("reindextriggered"),
        type: "success",
        position: "top-right",
    });
}

export async function upsertItem(apiUrl, item, itemStore, updateItems = false, params = {}, $t) {
    const { $axios } = useNuxtApp()

    let res;
    try {
        itemStore.savingItem = true;
        if (item.id) {
            res = (await $axios.patch(`${apiUrl}${item.id}/`, item, { "headers": authHeaders() })).data;
        } else {
            res = (await $axios.post(apiUrl, item, { "headers": authHeaders() })).data;
        }
        if (updateItems)
            await itemStore.retrieveItems(apiUrl, params);
        itemStore.savingItem = false;
    } catch (e) {
        ElNotification({
            title: "Error",
            message: $t("failedaction"),
            type: "error",
            position: "top-right",
        });
        throw e
    }
    ElNotification({
        title: "Success",
        message: $t("actionsuccess"),
        type: "success",
        position: "top-right",
    });
    return res;
}
