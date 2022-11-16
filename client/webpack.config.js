const webpack = require('webpack');
const path = require('path');
const { VueLoaderPlugin } = require('vue-loader');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const fs = require('fs').promises


module.exports = (webpackEnv) => {

  const env = process.env.NODE_ENV || 'dev'
  const debug = process.env.DEBUG ? parseInt(process.env.DEBUG) : 0

  const isProduction = env === 'production'
  const isDev = env === 'dev'
  var compiledPath = path.resolve(__dirname, 'static')
  if (webpackEnv.STATIC_PATH) {
    compiledPath = webpackEnv.STATIC_PATH
  }

  config = {
    // Environment.
    mode: isDev ? 'development' : 'production',
    // Entry javascript file.
    entry: [
      './src/entrypoint.js'
    ],
    // Output specific configurations. More info: https://webpack.js.org/configuration/output/
    output: {
      // Path where output compiled file will be stored.
      path: compiledPath,
      publicPath: '/static/',
      filename:  isDev ? '[name].js' : '[name].[contenthash].js',
      sourceMapFilename: isDev ? '[name].js.map' : '[name].[contenthash].js.map',
      assetModuleFilename: isDev ? 'assets/[name][ext]' : 'assets/[hash][ext]',
    },
    devtool: isDev || debug ? 'eval-source-map' : false,
    devServer: {
      // Automatically adds HotModuleReplacementPlugin for hot reloading
      hot: true,
      host: '0.0.0.0',
      port: '8087',
      historyApiFallback: {
        index: '/index.html'
      },
      devMiddleware: {
        writeToDisk: true,
      },
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
      },
      client: {
        // Prints compilation progress in percentage in the browser
        progress: true,
        // Shows a full-screen overlay in the browser
        overlay: true,
      },
      setupMiddlewares: (middlewares, devServer) => {
        if (!devServer) {
          throw new Error('webpack-dev-server is not defined');
        }
        middlewares.push(async (req, res) => {
          const html = await fs.readFile('./static/index.html')
          var htmlString = html.toString()
          for (const [key, value] of Object.entries(req.query)) {
            htmlString = htmlString.replace(`template.context.${key.toUpperCase()}`, JSON.stringify(value))
          }
          const reg = /template.context.*$/g
          htmlString = htmlString.replace(reg, '""')
          res.send(htmlString)
        });
        return middlewares;
      },
    },
    optimization: {
      // when the order of resolving is changed, the IDs will be changed as well
      // with deterministic option, despite any new local dependencies,
      // our vendor hash should stay consistent between builds
      moduleIds: 'deterministic',
      runtimeChunk: 'single',
      splitChunks: {
        minSize: 20000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          core: {
            test: /[\\/]src[\\/]core[\\/]/,
            name: 'core',
            chunks: 'all',
          },
        }
      },
    },
    module: {
      rules: [
        {
          test: /\.vue$/,
          loader: 'vue-loader'
        },
        {
          test: /\.js$/,
          use: [{ loader: 'babel-loader' }, { loader: 'core-env-loader' }],
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: [
            // Extract the style sheets into a dedicated file in production
            isDev ? 'vue-style-loader' :  MiniCssExtractPlugin.loader,
            { loader: 'css-loader', options: { sourceMap: isDev } },
          ]
        },
        {
          test: /\.less$/,
          use: [
            isDev ? 'vue-style-loader' :  MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader',
              options: {
                sourceMap: isDev,
              },
            },
            {
              loader: 'less-loader',
              options: {
                lessOptions: {
                  sourceMap: isDev,
                },
                additionalData: '@import "@dialpad/dialtone/build/less/dialtone.less";',
              },
            },
          ]
        },
        {
          test: /\.html$/,
          use: [{ loader: 'html-loader' }, { loader: 'core-env-loader' }],
        },
        {
          test: /\.md$/,
          loader: 'ignore-loader',
        },
        {
          test: /\.(png|ico|svg|jpg|jpeg|gif)$/i,
          type: 'asset/resource',
        },
      ],
    },
    plugins: [
      new CleanWebpackPlugin(),
      new webpack.optimize.LimitChunkCountPlugin({
        maxChunks: 6,
      }),
      ...(webpackEnv.ANALYZE ? [new BundleAnalyzerPlugin()] : []),
      new VueLoaderPlugin(),
      new HtmlWebpackPlugin({
        filename: 'index.html',
        template: 'index.html',
        inject: true
      }),
      new webpack.DefinePlugin({
        '__VUE_OPTIONS_API__': true,
        '__VUE_PROD_DEVTOOLS__': false,
      }),
      isDev ? new MiniCssExtractPlugin({
        filename: '[name].css',
      }) : new MiniCssExtractPlugin({
        filename: '[name].[contenthash].css',
      })
    ],
    resolveLoader: {
      alias: {
        'core-env-loader': path.resolve(__dirname, 'envLoader.js'),
      },
    },
    resolve: {
      extensions: ['.js', '.vue', '.css', '.less'],
      alias: {
        '@src': path.join(__dirname, 'src'),
        '@dialpad/dialtone/build': path.join(
          __dirname, 'node_modules', '@dialpad', 'dialtone', 'lib', 'build'
        ),
        '@dialpad/dialtone': path.join(
          __dirname, 'node_modules', '@dialpad', 'dialtone', 'lib', 'dist'
        ),
        '@components': path.join(__dirname, 'src', 'core', 'components'),
        'config': path.join(__dirname, 'src', 'core', 'config'),
        'logger': path.join(__dirname, 'src', 'core', 'logger'),
        'requests': path.join(__dirname, 'src', 'core', 'requests'),
        'helpers': path.join(__dirname, 'src', 'core', 'helpers'),
      },
    }
  }

  return config;
};
