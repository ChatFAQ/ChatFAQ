import {defineStore} from 'pinia';

function apiCacheName(apiUrl, params) {
    return apiUrl + new URLSearchParams(params).toString()
}

function authHeaders() {
    const token = useCookie('token').value
    return {
        'Authorization': `Token ${token}`
    }
}

export const useItemsStore = defineStore('items', {
    state: () => ({
        items: {},
        paths: {},
        schema: undefined,
        editing: undefined,
        adding: false,
        tableMode: false,
        loading: false,
        savingItem: false,
    }),
    actions: {
        async retrieveItems($axios, apiUrl = undefined, params = {}) {
            // Would be nice to amke ordering dynamic as a parameter, perhaps one day
            const cacheName = apiCacheName(apiUrl, params)
            let ordering = "-updated_date"
            if (apiUrl.indexOf("/people/") !== -1)
                ordering = "first_name"
            let url = apiUrl + `?ordering=${ordering}`
            if (Object.keys(params).length) {
                url += "&" + new URLSearchParams(params).toString()
            }
            this.items[cacheName] = (await $axios.get(url, {'headers': authHeaders()})).data
            return this.items[cacheName]
        },
        async deleteItem($axios, apiUrl, id) {
            await $axios.delete(`${apiUrl}${id}`, {'headers': authHeaders()})
            await this.retrieveItems($axios, apiUrl)
        },
        async loadSchema($axios) {
            if (!this.schema) {
                const openAPI = (await $axios.get('/back/api/schema/?format=json', {'headers': authHeaders()})).data
                this.schema = openAPI.components.schemas
                this.paths = openAPI.paths
            }
        },
        async getSchemaDef($axios, apiUrl, resolveRefs = true, _schemaName = undefined) {
            await this.loadSchema($axios)
            let schemaName = _schemaName
            if (!schemaName)
                schemaName = this.getSchemaNameFromPath(apiUrl)
            if (resolveRefs)
                return await this.resolveRefs($axios, this.schema[schemaName])
            return this.schema[schemaName]
        },
        async requestOrGetItem($axios, apiUrl, filter, params= {}, force = false) {
            const cacheName = apiCacheName(apiUrl, params)

            if (force || !this.items[cacheName]) {
                await this.retrieveItems($axios, apiUrl, params)
            }
            return this.items[cacheName].results.find(item => {
                for (const [key, val] of Object.entries(filter)) {
                    if (item[key] === null && val === null)
                        continue
                    if (item[key] !== null && item[key].toString() !== val.toString())
                        return false
                }
                return true
            })
        },
        async requestOrGetItems($axios, apiUrl, filter, params= {}, force = false) {
            const cacheName = apiCacheName(apiUrl, params)

            if (force || !this.items[cacheName]) {
                await this.retrieveItems($axios, apiUrl, params)
            }
            return this.items[cacheName].results.filter(item => {
                for (const [key, val] of Object.entries(filter)) {
                    if (item[key] === null && val === null)
                        continue
                    if (item[key] !== null && val !== null && item[key].toString() !== val.toString())
                        return false
                }
                return true
            })
        },
        async getNextItem($axios, apiUrl, itemId, direction = 1, params = {}, force= false) {
            const cacheName = apiCacheName(apiUrl, params)

            if (force || !this.items[cacheName]) {
                await this.retrieveItems($axios, apiUrl)
            }
            // It takes the next item after currentItem
            let index = this.items[cacheName].results.findIndex(item => item.id === itemId)
            if (index === -1)
                return undefined
            index += direction
            if (index < 0 || index >= this.items[cacheName].results.length)
                return undefined
            return this.items[cacheName].results[index]
        },
        async upsertItem($axios, apiUrl, item) {
            this.savingItem = true
            if (item.id) {
                await $axios.patch(`${apiUrl}${item.id}/`, item, {'headers': authHeaders()})
            } else {
                await $axios.post(apiUrl, item, {'headers': authHeaders()})
            }
            await this.retrieveItems($axios, apiUrl)
            this.savingItem = false
        },
        async resolveRefs($axios, schema) {
            if (!schema.properties && schema.oneOf) {
                const oneOf = await this.getSchemaDef($axios, undefined, false, schema.oneOf[0].$ref.split("/").slice(-1)[0])
                schema.properties = oneOf.properties
                schema.required = oneOf.required
            }
            for (const [propName, propInfo] of Object.entries(schema.properties)) {
                let ref = propInfo.$ref || propInfo.items?.$ref
                if (ref) {
                    const refName = ref.split("/").slice(-1)[0]
                    let obj = await this.getSchemaDef($axios, undefined, false, refName)
                    if (obj.enum)  {
                        propInfo.choices = obj.enum.map((choice) => ({label: choice, value: choice}))
                    } else if (obj.type === 'object') {
                        let items = await this.retrieveItems($axios, this.getPathFromSchemaName(refName))
                        items.results = items.results.map((item) => ({label: item.name, value: item.id}))  // Paginated choices
                        propInfo.choices = items
                    }
                }
            }
            return schema
        },
        stateToRead(){
            this.editing = undefined
            this.adding = undefined
        }
    },
    getters: {
        getPathFromSchemaName: (state) => (schemaName) => {
            for (const [path, pathInfo] of Object.entries(state.paths)) {
                if (pathInfo.get?.responses &&
                    pathInfo.get?.responses['200']?.content &&
                    (
                        pathInfo.get?.responses['200']?.content['application/json']?.schema?.items?.$ref === `#/components/schemas/${schemaName}` ||
                        pathInfo.get?.responses['200']?.content['application/json']?.schema?.$ref === `#/components/schemas/Paginated${schemaName}List` // Pagination object
                    )
                ) {
                    return path
                }
            }
        },
        getSchemaNameFromPath: (state) => (path) => {
            let ref = state.paths[path].get?.responses['200']?.content['application/json']?.schema?.$ref
            if (ref) {  // Pagination object
                ref = state.schema[ref.split("/").slice(-1)[0]].properties.results.items.$ref
                return ref.split("/").slice(-1)[0]
            }
            return state.paths[path].get?.responses['200']?.content['application/json']?.schema?.items?.$ref.split("/").slice(-1)[0]
        }
    }
});
