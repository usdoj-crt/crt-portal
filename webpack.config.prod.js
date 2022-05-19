const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  mode: 'production',
  devtool: 'source-map',
  entry: {
    actions: './crt_portal/static/js/actions.js',
    base: './crt_portal/static/js/base.js',
    commercialPublicLocation: './crt_portal/static/js/commercialPublicLocation.js',
    complaintView: './crt_portal/static/js/complaintView.js',
    dashboard: './crt_portal/static/js/dashboard.js',
    intakeBase: './crt_portal/static/js/intakeBase.js',
    hceResources: './crt_portal/static/js/hceResources.js',
    landing: './crt_portal/static/js/landing.js',
    privacy: './crt_portal/static/js/privacy.js',
    primaryComplaint: './crt_portal/static/js/primaryComplaint.js',
    proTemplate: './crt_portal/static/js/proTemplate.js',
    reportBase: './crt_portal/static/js/reportBase.js',
    reportClass: './crt_portal/static/js/reportClass.js',
    show: './crt_portal/static/js/show.js'
  },
  output: {
    filename: 'js/[name]-[chunkhash:8].js',
    path: path.resolve(__dirname, 'crt_portal/static/dist'),
    clean: true
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules)/,
        loader: 'babel-loader',
        options: { presets: ['@babel/env'] }
      },
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader']
      }
    ]
  },
  optimization: {
    minimizer: [new CssMinimizerPlugin()]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/style.css'
    }),
    new BundleTracker({ filename: './webpack-stats.json' })
  ]
};
