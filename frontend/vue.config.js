module.exports = {
  publicPath: '/',
  devServer: {
    port: 8081,
    historyApiFallback: true,
    open: true
  },
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'QuizMaster'  
    }
  }
}

