// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    entry: {
        index: path.join(__dirname, "src", "pages/index.js"),
        page1: path.join(__dirname, "src", "pages/page1.js"),
        page2: path.join(__dirname, "src", "pages/page2.js"),
    },
    output: {
      path:path.resolve(__dirname, "dist"),
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: "/templates/index.html",
        filename: "index.html",
      }),
      new HtmlWebpackPlugin({
        template: "/templates/page1.html",
        filename: "page1.html",
      }),
      new HtmlWebpackPlugin({
        template: "/templates/page2.html",
        filename: "page2.html",
      }),
    ],
    module: {
        rules: [
          {
            test: /\.?js$/,
            exclude: /node_modules/,
            use: {
              loader: "babel-loader",
              options: {
                presets: ['@babel/preset-env', '@babel/preset-react']
              }
            }
          },
          {
            test: /\.css$/,
            use: ['style-loader', 'css-loader'],
          },
        ]
      },
  devServer: {
    port: 3000,
  },
};
