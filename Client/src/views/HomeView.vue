<template>
  <div class="home">
    <div class="home-left">
      <div class="nev">
       <!-- <button style="width: 50px;" @click="bye">bey</button> -->
       <button class='btn' @click="newtalk">新建对话</button>
       <!-- <my-button @click="newtalk">新建对话</my-button> -->
       <br>
       <h4 class="text">历史记录</h4>
       <div class="ul_his">
        <ul style="display: flex; flex-direction: column; gap: 10px;">
          <li class="history"
          v-for="tag in tags"
          :key="tag.id"
          @click="history(tag)">
            {{tag.name}}
            <button class="delbutton" @click="deletehistory(tag)">
              <img src="../assets/删除.svg" alt="删除">
            </button>
          </li>
        </ul>
      </div>

      </div>
      <comic></comic>
    </div>
    <div class="home-right">

      <div class="right-version">
        <div class="llm-chat-demo">
          <span class="chat-demo">津小熊(您的天津本地生活助手)</span>
        </div>
      </div>

      <div class="right-body" :class="messages.length === 0 ? 'nodata' : ''" ref="messageContainer">
        <div v-for="(message, index) in messages" class="main-message" :key="index"
             :class="{'user-message': message.sender === 'User', 'Bear-message': message.sender === 'Bear'}">
          <!-- 消息发送者显示 -->
          <div class="message-sender"
               :class="{'user-message': message.sender === 'User', 'Bear-message': message.sender === 'Bear'}">
            <img v-if="message.sender === 'User'" src="../assets/Bear.svg" alt="User Icon">
            <img v-else-if="message.sender === 'Bear'" src="../assets/Bear.svg" alt="Bear Icon">
            <span class="message-sender-name"
                  :class="message.sender === 'User' ? 'user-color' : 'Bear-color'">{{ message.sender }}:</span>
          </div>

          <!-- 消息内容显示 -->
          <div v-if="message.sender === 'User'" class="user-message">{{ message.content }}</div>
          <div v-else class="Bear-message" v-html="message.content"></div>
        </div>
      </div>

      <div class="right-input" @keyup.enter="handleSearch">
        <!-- 输入框 -->
        <el-input v-model="queryKeyword" placeholder="开始和津小熊聊天吧~  (可以对我说:“你好津小熊”)" class="input"></el-input>
        <!-- 查询按钮 -->
        <el-button v-if="!loading" @click="handleSearch">
          <img  class="up-load" src="../assets/发送.svg">
        </el-button>
        <el-button v-if="loading" @click="closeEventSource">
          <img  class="up-load" src="../assets/等待.svg" >
        </el-button>
      </div>
      <div class="sec-notice">津小熊有时候也会犯错误噢，重要的问题请小主自己查证一下 </div>
    </div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it';
import markdownItFootnote from 'markdown-it-footnote';
import markdownItTaskLists from 'markdown-it-task-lists';
import markdownItAbbr from 'markdown-it-abbr';
import markdownItContainer from 'markdown-it-container';
import hljs from 'highlight.js';
import markdownItHighlightjs from 'markdown-it-highlightjs';
import Comic from '@/components/Comic.vue';

export default {
  name: 'HomeView',
  components: {Comic},
  computed: {
    // 将 Markdown 文本渲染为 HTML
    html() {
      return this.md.render(this.message);
    }
  },
  data() {
    return {
      md: new MarkdownIt()
          .use(markdownItFootnote)
          .use(markdownItTaskLists, {enabled: true})
          .use(markdownItAbbr)
          .use(markdownItContainer, 'warning')
          .use(markdownItHighlightjs, {hljs}), // 添加 markdown-it-highlightjs 插件

      tags: [
          { name: ' ', id:1 , his : "chatHistory1"},
          // { name: ' ', id:2 , his : "chatHistory2"},
          // { name: ' ', id:3 , his : "chatHistory3"},
          // { name: '', id:2 },
          // { name: '', id:3 },
          // { name: '', id:2 },
      ],
      // 存储用户输入
      queryKeyword: '',
      tempResult: {},
      loading: false,
      messages: [],
      socket: null,
      eventSource: null, // 添加事件源变量
      stopIcon: '../assets/等待.png',
      uploadIcon: '../assets/上传.png',

      //选择历史记录
      his_choose:'',

      //历史记录递增
      his_num: 1,
    }
  },
  methods: {
    newtalk(){
      this.his_num += 1;
      this.tags.push({ name:'', id:this.his_num , his : "chatHistory" + this.his_num});
    },
    bye(){
      this.$destroy();
    },
    deletehistory(tag){
      // this.his_num -= 1;
      this.tags.splice(this.tags.indexOf(tag), 1);

    },

    history(tag){
      this.his_choose = tag.his
      console.log(this.his_choose)
      console.log(localStorage.getItem(this.his_choose))
      try{
        let chatHistory = localStorage.getItem(this.his_choose);
        if (chatHistory === 'null' || chatHistory === null){
          this.messages = [];
          console.log("没有历史记录")

        }
        else{
          console.log(chatHistory);
          this.messages = JSON.parse(chatHistory);

        }

      }
      catch(error){
        console.log(error)
      }

    },

    async handleSearch() {
      // 如果正在加载中，则不执行新的搜索操作
      if (this.loading) {
        return;
      }

      const keyword = this.queryKeyword;
      this.loading = true;
      try {
        let zxakey = "zxa";
        // 初始化一个用于 SSE 的 message 对象
        let sseMessage = {
          orgcontent: '',
          content: '',
          sender: 'Bear',
          zxakey: zxakey
        };

        this.messages.push({
          content: keyword,
          sender: 'User'
        });

        //滚轮事件，使消息永远在底部
        this.$nextTick(() => {
          this.scrollToBottom();
        });

        let BearMessage = sseMessage;

        // 创建一个新的 EventSource 实例(每次后端发来消息即可收到)
        this.eventSource = new EventSource('http://127.0.0.1:5000/chat?query=' + keyword);
        // 设置消息事件监听器
        this.eventSource.onmessage = (event) => {
          try {

            //console.log(event.data);

            const dataObject = JSON.parse(event.data);
            // 判断是否为最后一个消息，如果是，则关闭事件源
            if (dataObject.message === 'done') {
              this.eventSource.close();
              this.loading = false;
            }

            if (dataObject.message != 'done') {
              // 累加接收到的数据到 BearMessage.orgcontent 中
              BearMessage.orgcontent += dataObject.message.toLocaleString();
              BearMessage.orgcontent = BearMessage.orgcontent.replace(/\*\*\s*([^*]*?)\s*(:\s*)?\*\*/g, '**$1$2**');
              //console.log(BearMessage.orgcontent)
              // 更新 BearMessage.content，这里假设 md.render 可以处理累加的字符串
              BearMessage.content = this.md.render(BearMessage.orgcontent);
            }
            this.scrollToBottom();
          } catch (e) {
            console.error('Error parsing JSON:', e);
          }
        };

        this.messages.push(sseMessage);
        this.queryKeyword = ''; // 清空输入框

        //历史数据存储
        console.log(this.messages)

        this.eventSource.onerror = error => {
          console.error('EventSource failed:', error);
          this.eventSource.close();
        };
      } catch (error) {
        console.error('发送消息时出错：', error);
      } finally {
      }
    },
    closeEventSource() {
      this.loading = false;
      if (this.eventSource) {
        this.eventSource.close();
      }
    },
    scrollToBottom() {
      const messageContainer = this.$refs.messageContainer;
      if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
      }
    },
  },

  mounted() {
    // this.messages = null
    this.tags = JSON.parse(localStorage.getItem('tags') || '[]');
    this.his_num = localStorage.getItem('his_num') ;
    console.log(this.messages)
    console.log(this.tags)
    if (this.tags !== null && this.messages !== null){
      for (let tag = 0; tag<this.tags.length; tag++){
        let chatHistory = localStorage.getItem(this.tags[tag].his);
        console.log(chatHistory);

        if (chatHistory !== null && chatHistory !== undefined && chatHistory !== 'null') {
          // console.log(chatHistory);
          this.messages = JSON.parse(chatHistory);
          console.log(this.messages);
          if (this.messages !== null){
              this.tags[tag].name = '';
              for (let i = 0; i < this.messages.length; i++) {
              if (this.messages[i].sender === 'User') {
                this.tags[tag].name += this.messages[i].content
              }
            }
          }
        }
        else{
          this.messages = [];
          console.log("没有历史记录")
        }
      }
  }

  },
  updated() {
    // if (this.tags !== null && this.messages !== null){
    //   for (let tag = 0; tag<this.tags.length; tag++){
    //     if (this.messages !== null){
    //               this.tags[tag].name = '';
    //               for (let i = 0; i < this.messages.length; i++) {
    //               if (this.messages[i].sender === 'User') {

    //                 this.tags[tag].name += this.messages[i].content
    //               }
    //             }
    //           }
    //     }
    //   }
  },
  beforeDestroy() {
      console.log(this.messages)
      localStorage.setItem(this.his_choose, JSON.stringify(this.messages));

      //存储tags
      localStorage.setItem('tags', JSON.stringify(this.tags));
      console.log(localStorage.getItem('tags'));

      //存储num
      localStorage.setItem('his_num', this.his_num);

      if (this.eventSource) {
        this.eventSource.close();
      }
    }
}
</script>

<style scoped>

@font-face {
  font-family: "Chat" ;
  src: url("../assets/Chat.ttf");
}

@font-face{
  font-family: 'Title';
  src: url("../assets/Title.ttf");
}

.home {
  background-color: #f8fddf;
  height: 100%;
  display: flex;
}

.home-left {
  width: 20%;
  background-color: #f4fdb8;
  display: flex;
}


.nev{
  width: 85%;
  height:60%;
  margin-left: 30px;

}

.newbutton{
  margin-top: 10px;
}

.text{
  font-family: 'Title';
  font-size: large;
}

.ul_his{
  width: 100%;
  height: 100%;
  overflow-y: auto; /* 添加垂直滚动条 */
}

ul > li:first-child {
  margin-top: -15px; /* 确保第一个 li 项没有额外的顶部间距 */
}

.history {
  position: relative;
  display: block;
  width: 100%;
  height: 75px;
  background-color: rgba(205, 214, 213, 0.326);
  font-family: 'Chat';
  font-size:15px;
  word-wrap: break-word;
  /* margin-bottom: 10px; */
  border: #f4fdb8;
  border-radius: 5px;
  overflow: hidden;
  text-overflow: ellipsis; /* 添加省略号 */
  letter-spacing: 2px;
}

.history:hover{
  background-color: rgba(206, 240, 255, 0.326);
}

.history:active {
 transform: translateY(-1px);
 box-shadow: 0 5px 10px rgba(179, 167, 167, 0.2);
}
.delbutton{
  border: 0ch;
  position: absolute;
  right: 0% ;
  bottom: 0%;
}

.delbutton:hover{
  background-color: rgba(205, 214, 213, 0.326);
}
.home-right {
  width: 80%;
}

.right-version {
  width: 80%;
  margin: auto;
  /* background-color: #f5fdc6; */
  height: 5%;
  display: flex;
  justify-content: start;
  align-items: center;
  border-radius: 15px;
  margin-bottom: 12px;
}


.llm-chat-demo {
  width: 68%;
  margin: auto;
  font-variation-settings: normal;
  font-weight: 550;
  font-size: 18px;
  cursor: pointer;
  color-scheme: light;
}

.chat-demo {
  font-family: 'Title',"SimHei", sans-serif;
  font-weight: 600;
  font-size: 20px;
  opacity: 0.8;
}

.right-body {
  height: 84%;
  overflow-y: auto;
}

.user-color {
  color: #000000;
}

.Bear-color {
  color: #000000;
}
.nodata {
  background-image: url("@/assets/HELLO.png");
  background-repeat: no-repeat;
  background-size: 35%;
  background-position: center 50%;
}

.main-message {
  margin: auto;
  width: 58%;
  justify-content: center;
}

.message-sender-name {
  margin-left: 10px;
  font-family: Söhne, ui-sans-serif, system;
  font-weight: 550;
  font-size: 18px;
}

.right-input {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 7%;

  position: relative;
}

.sec-notice {
  height: 4%;
  font-size: 12px;
  font-family: Söhne, ui-sans-serif;
  /* color: rgb(155, 155, 155); */
  display: flex;
  justify-content: center;
}

.input {
  width: 65%;
  margin-right: 5px;
}

.up-load {
  width: 32px;
}

::v-deep .el-button {
  padding: 5px 6px;
}

::v-deep .el-input__inner {
  font-family: 'Chat';
  font-weight: 500;
  height: 50px;
  border-radius: 15px;
  border: 1px solid #DCDFE6;
}

::v-deep .el-button--primary {
  position: relative;
  right: 3.5%;
  /* color: black !important; */

}

.user-message {
  font-family: 'Chat';
  font-weight: 500;
  text-align: left;
  padding: 5px;
  margin-bottom: 5px;
  border-radius: 15px;

}

.Bear-message {
  font-family: 'Chat';
  background-color: rgba(205, 214, 213, 0.326); /* 这里的 0.5 是透明度，你可以根据需要调整 */
  text-align: left;
  border-radius: 10px;
  padding: 5px;
  margin-bottom: 5px;
}

::v-deep .Bear-message pre .hljs {
  border-radius: 10px !important; /* 圆角 */
  background-color: #FAF7F7; /* 例子中的背景色 */
}

/* 设置滚动条的样式 */
::-webkit-scrollbar {
  width: 4px; /* 设置滚动条宽度 */
}

/* 设置滚动条轨道的样式 */
::-webkit-scrollbar-track {
  background: #f1f1f1; /* 设置滚动条轨道的背景色 */
}

/* 设置滚动条滑块的样式 */
::-webkit-scrollbar-thumb {
  background: #d9debb; /* 设置滚动条滑块的背景色 */
  border-radius: 3px; /* 设置滚动条滑块的圆角 */
}

/* 鼠标悬停时滚动条滑块的样式 */
::-webkit-scrollbar-thumb:hover {
  background: #b9e8f8; /* 设置鼠标悬停时滚动条滑块的背景色 */
}

.btn {
 margin-top: 10px;
 margin-left: 75px;
 position: relative;
 font-family: 'Title';
 font-size: 17px;
 text-transform: uppercase;
 text-decoration: none;
 padding: 1em 2.5em;
 display: inline-block;
 border-radius: 2em;
 transition: all .2s;
 border: none;
 font-weight: 500;
 color: black;
 background-color: rgba(252, 240, 0, 0.993);
}

.btn:hover {
 transform: translateY(-3px);
 box-shadow: 0 10px 20px rgba(156, 155, 151, 0.2);
}

.btn:active {
 transform: translateY(-1px);
 box-shadow: 0 5px 10px rgba(179, 167, 167, 0.2);
}

.btn::after {
 content: "";
 display: inline-block;
 height: 100%;
 width: 100%;
 border-radius: 100px;
 position: absolute;
 top: 0;
 left: 0;
 z-index: -1;
 transition: all .4s;
}

.btn::after {
 background-color: #fcffd4;
}

.btn:hover::after {
 transform: scaleX(1.4) scaleY(1.6);
 opacity: 0;
}
</style>
