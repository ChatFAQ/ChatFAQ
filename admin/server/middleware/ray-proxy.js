import {defineEventHandler} from 'h3'
import {createProxyMiddleware} from 'http-proxy-middleware'; // npm install http-proxy-middleware@beta

const rayProxyMiddleware = createProxyMiddleware('/ray/', {
    target: 'http://ray:8265',
    changeOrigin: true,
    ws: true,
    pathRewrite: {'^/ray/': ''},
    pathFilter: [
        '/ray/',
    ],
    logger: console
})

export default defineEventHandler(async (event) => {
    await new Promise((resolve, reject) => {
        const next = (err) =>
        {
            if (err) {
                reject(err)
            } else {
                resolve(true)
            }
        }

        rayProxyMiddleware(event.req, event.res, next)
    })
})
