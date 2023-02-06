<template>
    {{ count.foo.value + 1 }}
</template>

<script setup>
import { ref, onMounted } from "vue";

const count = { foo: ref(0) };

onMounted(() => {
    const div = document.createElement("div");
    div.classList.add("widget-iframe-wrapper");
    const iframe = document.createElement("iframe");
    iframe.src = "http://localhost:3000/widget";
    div.appendChild(iframe);
    document.body.appendChild(div);
});

</script>

<style>
.widget-iframe-wrapper {
    background-color: red;
}
</style>