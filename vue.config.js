module.exports = {
    publicPath: process.env.NODE_ENV === 'production' ? '/public/' : '/',
    chainWebpack: config => {
        config.module
            .rule('html')
            .test(/\.html$/)
            .use('html-loader')
            .loader('html-loader')
    }
};