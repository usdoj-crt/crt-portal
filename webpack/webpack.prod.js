const { merge } = require('webpack-merge');
const path = require('path');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'production',
  devtool: 'source-map',
  output: {
    filename: 'js/[name]-[chunkhash:8].js',
    path: path.resolve(__dirname, '../crt_portal/static/dist'),
    assetModuleFilename: 'assets/[name].[hash:8][ext]',
    clean: true
  }
});
