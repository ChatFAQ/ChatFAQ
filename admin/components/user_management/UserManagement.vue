<template>
    <div class="dashboard-page-title">{{ $t('usermanagement') }}</div>
    <el-tabs @tab-change="stateToRead" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('user')" name="user">
            <ReadWriteView readableName="User" apiUrl="/back/api/people/users/"
                           titleProp="first_name"
                           :cardProps="{
                    'email': $t('email'),
                }"
                           :tableProps="{
                    'email': $t('email'),
                }">
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('rolepermissions')" name="role-permissions">
            <ReadWriteView readableName="role" apiUrl="/back/api/people/groups/"
                           :cardProps="{
                    'name': $t('name'),
                }"
                           :tableProps="{
                    'name': $t('name'),
                }">
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import { useItemsStore } from "~/store/items.js";

const { $axios } = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("user")
await itemsStore.loadSchema($axios)

function stateToRead(tabName, event) {
    itemsStore.adding = false
    itemsStore.editing = undefined
}

</script>
