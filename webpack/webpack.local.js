const { merge } = require('webpack-merge');
const path = require('path');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'source-map',
  output: {
    filename: 'js/[name].js',
    path: path.resolve(__dirname, '../crt_portal/static/dist'),
    assetModuleFilename: 'assets/[name][ext]',
    clean: true
  }
});
