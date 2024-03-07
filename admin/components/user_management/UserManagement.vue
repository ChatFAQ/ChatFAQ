<template>
    <div class="dashboard-page-title">{{ $t('usermanagement') }}</div>
    <el-tabs class="main-page-tabs" @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :label="$t('user')" name="user">
            <ReadWriteView
                :readableName="$t('user')"
                apiUrl="/back/api/people/users/"
                :titleProps="['first_name', 'last_name']"
                :cardProps="{
                    'email': $t('email'),
                }"
                :tableProps="{
                    'email': {'name': $t('email')},
                }"
                :excludeFields="['date_joined', 'last_login', 'rpc_group']"
                @submitFormStart="submitPassword"
                :sections="{
                    [$t('userinformation')]: [
                        'first_name',
                        'last_name',
                        'email',
                        'password',
                    ],
                    [$t('userpermissions')]: [
                        'is_active',
                        'is_staff',
                        'is_superuser',
                        'groups',
                        'user_permissions',
                    ]
                }"
            >
                <template v-slot:write-password="props">
                    <Password :form="props.form" :fieldName="props.fieldName" ref="password"/>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :label="$t('grouppermissions')" name="group-permissions">
            <ReadWriteView :readableName="$t('group')" apiUrl="/back/api/people/groups/"
                           :cardProps="{
                }"
                           :tableProps="{
                    'name': { 'name': $t('name') },
                }">
            </ReadWriteView>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import ReadWriteView from "~/components/generic/ReadWriteView.vue";
import { useItemsStore } from "~/store/items.js";
import Password from "~/components/user_management/fields/Password.vue";

const password = ref(null)

const { $axios } = useNuxtApp();

const itemsStore = useItemsStore()

const itemType = ref("user")
await itemsStore.loadSchema($axios)


function submitPassword() {
    password.value.submit()
}
</script>
