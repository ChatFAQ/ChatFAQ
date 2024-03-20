import {defineStore} from 'pinia';

export function authHeaders() {
    const token = useCookie('token').value
    return {
        'Authorization': `Token ${token}`
    }
}

export const useItemsStore = defineStore('items', {
    state: () => ({
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
        itemsChanged: 0,
        total: 0
    }),
    actions: {
        async retrieveItems(apiUrl = undefined, params = {}, one= false) {
            const {$axios} = useNuxtApp();

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
            if (one) {
                return res.results[0]
            }
            return res
        },
        async deleteItem(apiUrl, id, refresh = true) {
            const {$axios} = useNuxtApp();

            await $axios.delete(`${apiUrl}${id}`, {'headers': authHeaders()})
            if (refresh)
                await this.retrieveItems(apiUrl)
        },
        async loadSchema() {
            const {$axios} = useNuxtApp();

            if (!this.schema) {
                const openAPI = (await $axios.get('/back/api/schema/?format=json', {'headers': authHeaders()})).data
                this.schema = openAPI.components.schemas
                this.paths = openAPI.paths
            }
        },
        async getSchemaDef(apiUrl, resolveRefs = true, _schemaName = undefined) {
            await this.loadSchema()
            let schemaName = _schemaName
            if (!schemaName)
                schemaName = this.getSchemaNameFromPath(apiUrl)
            if (resolveRefs)
                return await this._resolveRefs(this.schema[schemaName])
            return this.schema[schemaName]
        },
        async getNextItem(items, apiUrl, itemId, direction = 1, params = {}, force= false) {
            if (force || !items) {
                items = await this.retrieveItems(apiUrl)
            }
            // It takes the next item after currentItem
            let index = items.results.findIndex(item => item.id === itemId)
            if (index === -1)
                return undefined
            index += direction
            if (index < 0 || index >= items.results.length)
                return undefined
            return items.results[index]
        },
        async _resolveRefs(schema) {
            if (!schema.properties && schema.oneOf) {
                const oneOf = await this.getSchemaDef(undefined, false, schema.oneOf[0].$ref.split("/").slice(-1)[0])
                schema.properties = oneOf.properties
                schema.required = oneOf.required
            }
            for (const [propName, propInfo] of Object.entries(schema.properties)) {
                let ref = propInfo.$ref || propInfo.items?.$ref
                if (ref) {
                    const refName = ref.split("/").slice(-1)[0]
                    let obj = await this.getSchemaDef(undefined, false, refName)
                    if (obj.enum)  {
                        propInfo.choices = obj.enum.map((choice) => ({label: choice, value: choice}))
                    } else if (obj.type === 'object') {
                        let items = await this.retrieveItems(this.getPathFromSchemaName(refName))
                        items = JSON.parse(JSON.stringify(items))  // Deep copy
                        items.results = items.results.map((item) => ({label: item.name, value: item.id}))  // Paginated choices
                        propInfo.choices = items
                    }
                }
            }
            return schema
        },
        stateToRead(){
            if (this.editing === undefined && this.adding === undefined && this.currentPage === 1 && Object.keys(this.filters).length === 0)
                return
            this.editing = undefined
            this.adding = undefined
            this.currentPage = 1
            this.filters = {}
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
