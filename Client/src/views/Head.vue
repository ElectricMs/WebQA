<template>

<div id="app">


    <header>
      <img src="../assets/schoolSymbol.png" alt="Logo" class="logo" />
      <h1>软件学院企业实训第八组</h1>
    </header>
    <main>
      <section class="introduction">
        <h2>天津本地智能问答系统</h2>
        <p>立即体验本地智能问答系统，为您提供便捷的本地生活服务。</p>
      </section>
      <section class="action-buttons">
        <router-link to="/conversation" class="button">立即体验→</router-link>
        <router-link to="/login" class="button">登录</router-link>
      </section>
    </main>

  </div>

</template>
<script>

</script>



<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}

.background {

  position: absolute;

  display: block;

  top: 0;

  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}
header {

  display: flex;
  align-items: center;
  margin-top: -20px;
  padding: 20px;
}

.logo {
  margin-right: 10px; /* 调整图片与文字之间的间距 */

  width: 100px; /* 设置图片宽度为100像素 */
  height: auto; /* 高度自动，保持图片的宽高比 */
}

h1 {
  margin: 0;
  font-size: 1.5em; /* 根据需要调整标题大小 */
}
h2{
  font-size: 3em;
}
main {
  margin: 15px;
  margin-top: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  height:50vh;
  flex-direction: column;
}

.introduction {
  margin-bottom: 20px;
}
.button{
  transition: background-color 0.3s;
  font-weight: 600;
  font-size: 22px;
  line-height: 31px;
  letter-spacing: 0;
  width: 160px;
  height: auto;
  padding:10px 0px;
  background: #2454ff;
  cursor: pointer;
  border-radius: 8px;


}


.action-buttons a {
  font-size: 20px;
  margin: 0 50px;
  color: #fff;
  background-color:blue;


  text-decoration: none;
}

.action-buttons a:hover {
  background-color: limegreen;
}
.action-buttons{
  margin-top: 40px;
  display: flex; /* 使用Flexbox布局 */

  gap: 10px; /* 按钮之间的间隔 */
  justify-content: center;

  align-items: center;

}
</style>
