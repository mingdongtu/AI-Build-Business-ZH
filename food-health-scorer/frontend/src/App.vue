<template>
  <div id="app">
    <header>
      <h1>食品健康评分系统</h1>
    </header>
    <main>
      <router-view />
    </main>
    <footer>
      <p>© {{ new Date().getFullYear() }} 食品健康评分系统</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

header {
  margin-bottom: 30px;
}

footer {
  margin-top: 30px;
  font-size: 14px;
  color: #666;
}
</style>
