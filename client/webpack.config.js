var path = require('path');

const ExtractTextPlugin = require('extract-text-webpack-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');

module.exports = {
  entry: './javascripts/index.js',
  output: {
      filename: 'js/app.js',
      path: path.resolve(__dirname)
  },
  module: {
    rules: [
      {
        test: /\.styl|css$/,
        use: ExtractTextPlugin.extract([
          'css-loader',
          'stylus-loader'
        ])
      }
    ]
  },
  plugins: [
    new ExtractTextPlugin({
      filename: 'css/style.css',
    }),
    new OptimizeCssAssetsPlugin()
  ],
};
