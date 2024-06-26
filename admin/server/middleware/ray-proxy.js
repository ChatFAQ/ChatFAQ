import {defineEventHandler} from 'h3'
import {createProxyMiddleware} from 'http-proxy-middleware';
import * as path from "path"; // npm install http-proxy-middleware@beta

const rayProxyMiddleware = createProxyMiddleware('/ray/', {
    target: 'http://back:8265',
    changeOrigin: true,
    ws: true,
    pathRewrite: {'^/ray/': ''},
    pathFilter: [
        '/ray/',
    ],
    logger: console
})

function extractTokenFromRawHeaders(rawHeaders) {
    let cookieIndex = rawHeaders.indexOf('cookie')  // dev server
    if (cookieIndex === -1)
        cookieIndex = rawHeaders.indexOf('Cookie')  // prod server
    const cookieValue = rawHeaders[cookieIndex + 1];
    if (cookieValue.indexOf(' token=') === -1)
        return null;
    let token = cookieValue.split(' token=')[1];
    token = token.split(';')[0];
    return token;
}

async function isAuthorized(event) {
    const token = extractTokenFromRawHeaders(event.node.req.rawHeaders)
    if (!token)
        return false

    const options = {
        headers: {
            'Authorization': `Token ${token}`,
        }
    };
    try {
        await $fetch(path.posix.join(process.env.NUXT_API_URL, 'back/api/people/people/'), options)
    } catch (e) {
        return false
    }
    return true
}

export default defineEventHandler(async (event) => {
    if (!event.node.req.url.startsWith('/ray/'))
        return
    if (!await isAuthorized(event))
        return

    await new Promise((resolve, reject) => {
        const next = (err) => {
            if (err) {
                reject(err)
            } else {
                resolve(true)
            }
        }
        rayProxyMiddleware(event.node.req, event.node.res, next)

    })
})
