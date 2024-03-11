import {defineStore} from 'pinia';

function apiCacheName(apiUrl, params) {
    return apiUrl
    return apiUrl + new URLSearchParams(params).toString()
}

export function authHeaders() {
    const token = useCookie('token').value
    return {
        'Authorization': `Token ${token}`
    }
}

export const useItemsStore = defineStore('items', {
    state: () => ({
        items: {},
        paths: {},
        filters: {},
        schema: undefined,
        editing: undefined,
        adding: false,
        tableMode: false,
        loading: false,
        savingItem: false,
        pageSize: 50,
        currentPage: 1,
        ordering: undefined,
    }),
    actions: {
        async retrieveItems($axios, apiUrl = undefined, params = {}, cache= true, one= false) {
            const cacheName = apiCacheName(apiUrl, params)
            // Would be nice to amke ordering dynamic as a parameter, perhaps one day
            if (!("limit" in params))
                params.limit = this.pageSize
            if (!("offset" in params))
                params.offset = (this.currentPage - 1) * this.pageSize
            if (!("ordering" in params)) {
                params.ordering = this.ordering
            }
            // add this.filter into params:
            for (const [key, val] of Object.entries(this.filters)) {
                if (params[key] === undefined)
                    params[key] = val
            }
            apiUrl += "?" + new URLSearchParams(params).toString()

            let res = (await $axios.get(apiUrl, {'headers': authHeaders()})).data
            if (Array.isArray(res)) { // When the endpoint is not paginated
                res = {results: res}
            }
            if (!cache) {
                if (one) {
                    return res.results[0]
                }
                return res
            }

            this.items[cacheName] = res
            if (one) {
                return this.items[cacheName][0]
            }
            return this.items[cacheName]
        },
        async deleteItem($axios, apiUrl, id, refresh = true) {
            await $axios.delete(`${apiUrl}${id}`, {'headers': authHeaders()})
            if (refresh)
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
        async upsertItem($axios, apiUrl, item, params = {}) {
            this.savingItem = true
            let res
            if (item.id) {
                res = await $axios.patch(`${apiUrl}${item.id}/`, item, {'headers': authHeaders()})
            } else {
                res = await $axios.post(apiUrl, item, {'headers': authHeaders()})
            }
            await this.retrieveItems($axios, apiUrl, params)
            this.savingItem = false
            return res
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
                        items = JSON.parse(JSON.stringify(items))  // Deep copy
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
            this.currentPage = 1
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
