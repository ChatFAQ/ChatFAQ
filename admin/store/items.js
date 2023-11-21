import {defineStore} from 'pinia';


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
        async getSchemaDef($axios, schemaName, resolveRefs = true) {
            await this.loadSchema()
            if (resolveRefs)
                return await this.resolveRefs($axios, this.schema[schemaName])
            return this.schema[schemaName]
        },
        async requestOrGetItem($axios, schemaName, id) {
            if (!this.items[schemaName]) {
                await this.retrieveItems($axios, schemaName)
            }
            return this.items[schemaName].find(item => item.id === parseInt(id))
        },
        async resolveRefs($axios, schemaT) {
            for (const [propName, propInfo] of Object.entries(schemaT.properties)) {
                if (propInfo.$ref) {
                    const refName = propInfo.$ref.split("/").slice(-1)[0]
                    let obj = await this.getSchemaDef($axios, refName, false)
                    if (obj.enum)  {
                        propInfo.choices = obj.enum.map((choice) => ({label: choice, value: choice}))
                    } else if (obj.type === 'object') {
                        let items = await this.retrieveItems($axios, refName)
                        propInfo.choices = items.map((item) => ({label: item.name, value: item.id}))
                    }
                }
            }
            return schemaT
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
