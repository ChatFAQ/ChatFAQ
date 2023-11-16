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
    }),
    actions: {
        async retrieveItems($axios, itemType) {
            this.items[itemType] = (await $axios.get(`/back/api/language-model/${itemType}/`)).data
        },
        async requestOrGetSchema($axios, schemaName) {
            if (!this.schema) {
                this.schema = resolveRefs(
                    (await $axios.get('/back/api/schema/?format=json')).data.components.schemas
                )
            }
            return this.schema[schemaName]
        }
    }
});
