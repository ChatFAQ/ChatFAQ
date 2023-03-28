<template>
    <Widget :chatfaqWs="chatfaqWS" :chatfaqApi="chatfaqAPI" :fsmDef="fsmDef" :userId="userId" :title="title" :subtitle="subtitle"/>
</template>
<script setup>
function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

let userId = localStorage.getItem("chatfaq-user-identifier")
if(!userId) {
    localStorage.setItem("chatfaq-user-identifier", uuidv4())
    userId = localStorage.getItem("chatfaq-user-identifier")
}

const { public: { chatfaqWS, chatfaqAPI } } = useRuntimeConfig()
console.log("PUBLIC CONFIG:::")
console.log(chatfaqWS)
console.log(chatfaqAPI)
console.log(":::")
const title = ref("Hello there 👋")
const subtitle = ref("How can we help you?")
const fsmDef = ref("simple_fsm")

</script>
