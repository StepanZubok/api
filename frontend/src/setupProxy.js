// const { createProxyMiddleware } = require('http-proxy-middleware');

// module.exports = function (app) {
//   app.use(
//     '/api',
//     createProxyMiddleware({
//       target: 'http://192.168.1.250:8000',
//       changeOrigin: true,
//       pathRewrite: { '^/api': '' },
//       cookieDomainRewrite: { '*': 'localhost' },
//       cookiePathRewrite: { '*': '/' },
//       onProxyReq: (proxyReq, req) => {
//         const cookies = req.headers.cookie;
//         console.log(`[→] ${req.method} ${req.url} | Cookies: ${cookies ? 'YES' : 'NO'}`);
//         if (cookies) proxyReq.setHeader('cookie', cookies);
//       },
//       onProxyRes: (proxyRes, req) => {
//         const setCookie = proxyRes.headers['set-cookie'];
//         console.log(`[←] ${proxyRes.statusCode} ${req.url}${setCookie ? ' | Set-Cookie' : ''}`);
//       },
//     })
//   );
// };