<template>
    <div class="dashboard-page-title">{{ $t('usermanagement') }}</div>
    <el-tabs @tab-change="itemsStore.stateToRead" v-model="itemType">
        <el-tab-pane :lazy="true" :label="$t('user')" name="user">
            <ReadWriteView
                :readableName="$t('user')"
                apiUrl="/back/api/people/users/"
                titleProp="first_name"
                :cardProps="{
                    'email': $t('email'),
                }"
                :tableProps="{
                    'email': $t('email'),
                }"
                :excludeFields="['date_joined', 'last_login', 'rpc_group']"
                @submitForm="submitPassword"
                :sections="{
                    [$t('userinformation')]: [
                        'first_name',
                        'last_name',
                        'email',
                        'password',
                    ],
                    [$t('userpermissions')]: [
                        'is_active',
                        'groups',
                        'user_permissions',
                    ]
                }"
            >
                <template v-slot:password="props">
                    <Password :form="props.form" :fieldName="props.fieldName" ref="password"/>
                </template>
            </ReadWriteView>
        </el-tab-pane>
        <el-tab-pane :lazy="true" :label="$t('rolepermissions')" name="role-permissions">
            <ReadWriteView :readableName="$t('role')" apiUrl="/back/api/people/groups/"
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
