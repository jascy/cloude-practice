<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <router-link to="/" class="logo">📚 问答知识库</router-link>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="$route.path"
          class="header-menu"
        >
          <el-menu-item index="/">
            <el-icon><Search /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/import">
            <el-icon><Upload /></el-icon>
            <span>导入</span>
          </el-menu-item>
          <el-menu-item index="/manage">
            <el-icon><Setting /></el-icon>
            <span>管理</span>
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  height: 60px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  text-decoration: none;
  white-space: nowrap;
}

.header-menu {
  border-bottom: none !important;
}

.app-main {
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
  padding: 20px;
}
</style>
