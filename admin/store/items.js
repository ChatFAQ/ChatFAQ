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
        paths: {},
        schema: undefined,
        editing: undefined,
        adding: false,
    }),
    actions: {
        async retrieveItems($axios, schemaName) {
            const url = this.getPathFromSchemaName(schemaName)
            this.items[schemaName] = (await $axios.get(url)).data
            return this.items[schemaName]
        },
        async deleteItem($axios, schemaName, id) {
            const url = this.getPathFromSchemaName(schemaName)
            await $axios.delete(`${url}${id}`)
            await this.retrieveItems($axios, schemaName)
        },
        async loadSchema($axios) {
            if (!this.schema) {
                const openAPI = (await $axios.get('/back/api/schema/?format=json')).data
                this.schema = openAPI.components.schemas
                this.paths = openAPI.paths
            }
        },
        async getSchemaDef($axios, schemaName) {
            await this.loadSchema()
            return this.schema[schemaName]
        },
        async requestOrGetItem($axios, schemaName, id) {
            if (!this.items[schemaName]) {
                await this.retrieveItems($axios, schemaName)
            }
            return this.items[schemaName].find(item => item.id === parseInt(id))
        }
    },
    getters: {
        getPathFromSchemaName: (state) => (schemaName) => {
            for (const [path, pathInfo] of Object.entries(state.paths)) {
                if (pathInfo.get?.responses &&
                    pathInfo.get?.responses['200']?.content &&
                    pathInfo.get?.responses['200']?.content['application/json']?.schema?.items?.$ref === `#/components/schemas/${schemaName}`) {
                    return path
                }
            }
        }
    }
});
