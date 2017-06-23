var path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');

module.exports = {
  entry: './builder/static/javascripts/index.js',
  output: {
      filename: 'js/app.js',
      path: path.resolve(__dirname, 'builder/static')
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ExtractTextPlugin.extract(
          {
              fallback: 'style-loader',
              use: 'css-loader'
          }
        )
      }
    ]
  },
  plugins: [
    new ExtractTextPlugin({
      filename: 'css/style.css',
    }),
    new OptimizeCssAssetsPlugin()
  ]
};
