import {defineStore} from 'pinia';

function resolveRefs(schema) {

    for (const value of Object.values(schema)) {
        if(!value.properties)
            continue
        for (const [propName, propInfo] of Object.entries(value.properties)) {
            if (propInfo.$ref) {
                let obj = schema[propInfo.$ref.replace('#/components/schemas/', '')]
                if (obj.enum)  {
                    propInfo.choices = obj.enum
                } else if (obj.type === 'object') {
                    propInfo.remote = obj
                }
            }
        }
    }
    return schema
}

export const useItemsStore = defineStore('items', {
    state: () => ({
        items: {},
        schema: undefined,
        editing: undefined,
        adding: false,
    }),
    actions: {
        async retrieveItems($axios, apiName) {
            this.items[apiName] = (await $axios.get(`/back/api/language-model/${apiName}/`)).data
        },
        async deleteItem($axios, apiName, id) {
            await $axios.delete(`/back/api/language-model/${apiName}/${id}`)
            await this.retrieveItems($axios, apiName)
        },
        async requestOrGetSchema($axios, schemaName) {
            if (!this.schema) {
                this.schema = resolveRefs(
                    (await $axios.get('/back/api/schema/?format=json')).data.components.schemas
                )
            }
            return this.schema[schemaName]
        },
        async requestOrGetItem($axios, apiName, schemaName, id) {
            if (!this.items[apiName]) {
                await this.retrieveItems($axios, apiName)
            }
            return this.items[apiName].find(item => item.id === parseInt(id))
        }
    }
});
