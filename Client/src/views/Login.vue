<template>
  <div class="top-container">
    <div class="shell">
        <div class="container a-container" id="a-container">
            <form class="form" id="a-form">
                <h2 class="form_title title">创建账号</h2>
                <div class="form_icons">
                    <i class="iconfont icon-QQ"></i>
                    <i class="iconfont icon-weixin"></i>
                    <i class="iconfont icon-bilibili-"></i>
                </div>
                <span class="form_span">选择注册方式或电子邮箱注册</span>
              <el-form class="form2" :model="ruleForm" :rules="rules" ref="ruleForm" label-width="100px" size="medium" >

                <el-form-item  prop="email">
                  <el-input class="form_input" v-model="ruleForm.email" placeholder="Email"></el-input>
                </el-form-item>
                <el-form-item prop="password">
                  <el-input class="form_input" type="password" v-model="ruleForm.password" placeholder="Password" ></el-input>
                </el-form-item>
                <el-form-item prop="checkPass">
                  <el-input class="form_input" type="password" v-model="ruleForm.checkPass" placeholder="Confirm Password"></el-input>
                </el-form-item>

              </el-form>
                <button class="form_button button submit" @click="handleClick('ruleForm')">SIGN UP</button>
            </form>
        </div>

        <div class="container b-container" id="b-container">
            <form action="" method="" class="form" id="b-form">
                <h2 class="form_title title">登入账号</h2>
                <div class="form_icons">
                    <i class="iconfont icon-QQ"></i>
                    <i class="iconfont icon-weixin"></i>
                    <i class="iconfont icon-bilibili-"></i>
                </div>
                <span class="form_span">选择登录方式活电子邮箱登录</span>
                <el-form class="form2" :model="ruleForm" :rules="rules" ref="ruleForm" label-width="100px" size="medium" >

                <el-form-item  prop="email">
                  <el-input class="form_input" v-model="ruleForm.email" placeholder="Email"></el-input>
                </el-form-item>

                <el-form-item  prop="password">
                  <el-input class="form_input" type="password" v-model="ruleForm.password" placeholder="Password"></el-input>
                </el-form-item>
              </el-form>
                <a class="form_link">忘记密码？</a>
                <button class="form_button button submit" @click="handleClick2('ruleForm')">SIGN IN</button>
            </form>
        </div>

        <div class="switch" id="switch-cnt">
            <div class="switch_circle"></div>
            <div class="switch_circle switch_circle-t"></div>
            <div class="switch_container" id="switch-c1">
                <h2 class="switch_title title" style="letter-spacing: 0;">Welcome Back！</h2>
                <p class="switch_description description">已经有账号了嘛，去登入账号来进入奇妙世界吧！！！</p>
                <button class="switch_button button switch-btn">SIGN IN</button>
            </div>

            <div class="switch_container is-hidden" id="switch-c2">
                <h2 class="switch_title title" style="letter-spacing: 0;">Hello Friend！</h2>
                <p class="switch_description description">去注册一个账号，成为尊贵的粉丝会员，让我们踏入奇妙的旅途！</p>
                <button class="switch_button button switch-btn">SIGN UP</button>
            </div>
        </div>
    </div>
  </div>

</template>
<script>
import '../css/iconfont.css'
import Vue from 'vue';
import axios from 'axios';
export default {
  data() {
    var validatePass2 = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请再次输入密码'));
        } else if (value !== this.ruleForm.password) {
          callback(new Error('两次输入密码不一致!'));
        } else {
          callback();
        }
      };
    return {
      ruleForm: {

        email:'',
        password: '',
        checkPass: '',
      },
      rules: {

        password: [
          {required: true, message: '密码格式不正确', trigger: 'blur'},
          {min: 3, max: 10, message: '长度在 3 到 10 个字符', trigger: 'blur'}
        ],
        email: [
          {required: true,type: 'email', message: '邮箱格式不正确', trigger: 'blur'},
          {
            //邮箱规范
          }
        ],
        checkPass:[
             { validator: validatePass2, trigger: 'blur' }
        ]
      },
      // 定义响应式数据
      switchCtn: null,
      switchC1: null,
      switchC2: null,
      switchCircle: null,
      switchBtn: null,
      aContainer: null,
      bContainer: null,
      allButtons: null
    };
  },
  methods: {
    //注册
    handleClick(formName) {
    this.submitForm(formName);
    this.resetForm(formName);
  },
    //登录
    handleClick2(formName) {
    this.submitForm_login(formName);
    this.resetForm(formName);
  },
    submitForm_login(formName){
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          const email = this.ruleForm.email;
          const password = this.ruleForm.password;
          console.log('Email:', email);
          console.log('Password:', password);
          try {
            const newLogin = {
              account: email,
              password: password
            };
            const response = await axios.post('http://127.0.0.1:5000/login', newLogin);
            if (response.status === 200) {
              alert('登录成功!');
              console.log('User login:', response.data);
              localStorage.setItem('token',response.data.token)
              await this.$router.push('/conversation');
            } else {
              console.error('Failed to login:', response.status);
            }
          }catch(error){
            if (error.response) {
          // 请求已发出，服务器响应了状态码
              alert("账户或密码错误！")
          console.error('Error response:', error.response.data);
          // 这里可以根据 error.response.data.detail 显示具体的错误信息
        } else if (error.request) {
          // 请求已发出但没有收到响应
          console.error('No response:', error.request);
        } else {
          // 发生了触发请求错误的问题
          console.error('Error:', error.message);
        }
          }




        } else {
          alert('输入的信息格式错误!!');
          return false;
        }
      });
    },
    submitForm(formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          const email = this.ruleForm.email;
          const password = this.ruleForm.password;
          console.log('Email:', email);
          console.log('Password:', password);
          try {
            const newUser = {
              account: email,
              password: password
            };
            const response = await axios.post('http://127.0.0.1:5000/signup', newUser);
            if (response.status === 200) {
              alert('注册成功');
              console.log('User registered:', response.data);
            } else {
              console.error('Failed to register:', response.status);
            }
          }catch(error){
            if (error.response) {
              // 请求已发出，服务器响应了状态码
              alert("Account already registered")
              console.error('Error response:', error.response.data);
              // 这里可以根据 error.response.data.detail 显示具体的错误信息
            } else if (error.request) {
              // 请求已发出但没有收到响应
              console.error('No response:', error.request);
            } else {
              // 发生了触发请求错误的问题
              console.error('Error:', error.message);
          }
          }




        } else {
          alert('输入的信息格式错误!!');
          return false;
        }
      });
    },
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    getButtons(e) {
      e.preventDefault();
    },
    changeForm() {
      // 修改类名
      this.switchCtn.classList.add("is-gx");
      setTimeout(() => {
        this.switchCtn.classList.remove("is-gx");
      }, 1500);
      this.switchCtn.classList.toggle("is-txr");
      this.switchCircle[0].classList.toggle("is-txr");
      this.switchCircle[1].classList.toggle("is-txr");

      this.switchC1.classList.toggle("is-hidden");
      this.switchC2.classList.toggle("is-hidden");
      this.aContainer.classList.toggle("is-txl");
      this.bContainer.classList.toggle("is-txl");
      this.bContainer.classList.toggle("is-z");
    },


  },
  mounted() {
    // 组件挂载后，获取 DOM 元素
    this.$nextTick(() => {
      this.switchCtn = this.$el.querySelector("#switch-cnt");
      this.switchC1 = this.$el.querySelector("#switch-c1");
      this.switchC2 = this.$el.querySelector("#switch-c2");
      this.switchCircle = this.$el.querySelectorAll(".switch_circle");
      this.switchBtn = this.$el.querySelectorAll(".switch-btn");
      this.aContainer = this.$el.querySelector("#a-container");
      this.bContainer = this.$el.querySelector("#b-container");
      this.allButtons = this.$el.querySelectorAll(".submit");

      // 为按钮添加事件监听器
      [].forEach.call(this.allButtons, button => button.addEventListener("click", this.getButtons));
      [].forEach.call(this.switchBtn, button => button.addEventListener("click", this.changeForm));
    });
  },
  beforeDestroy() {
    // 确保在组件销毁前移除事件监听器
    [].forEach.call(this.allButtons, button => button.removeEventListener("click", this.getButtons));
    [].forEach.call(this.switchBtn, button => button.removeEventListener("click", this.changeForm));
  }
};
</script>
<style scoped>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            /* 字体无法选中 */
            user-select: none;
        }

        .top-container {
            width: 100%;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 12px;
            background-color: #606568;

        }


        .shell {
            position: relative;
            width: 1000px;
            min-width: 1000px;
            min-height: 600px;
            height: 600px;
            padding: 25px;
            background-color: #ecf0f3;

            border-radius: 12px;
            overflow: hidden;
        }

        /* 设置响应式 */
        @media (max-width: 1200px) {
            .shell {
                transform: scale(0.7);
            }
        }

        @media (max-width: 1000px) {
            .shell {
                transform: scale(0.6);
            }
        }

        @media (max-width: 800px) {
            .shell {
                transform: scale(0.5);
            }
        }

        @media (max-width: 600px) {
            .shell {
                transform: scale(0.4);
            }
        }

        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            position: absolute;
            top: 0;
            width: 600px;
            height: 100%;
            padding: 25px;
            background-color: #ecf0f3;
            transition: 1.25s;
        }

        .form {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            width: 100%;
            height: 100%;
        }
        .form2{
          margin-left: -100px;
        }
        .iconfont {
            margin: 0 5px;
            border: rgba(0, 0, 0, 0.5) 2px solid;
            border-radius: 50%;
            font-size: 25px;
            padding: 3px;
            opacity: 0.5;
            transition: 0.1s;
        }

        .iconfont:hover {
            opacity: 1;
            transition: 0.15s;
            cursor: pointer;
        }



        .form_span {
            margin-top: 30px;
            margin-bottom: 12px;
        }

        .form_link {
            color: #181818;
            font-size: 15px;
            margin-top: 25px;
            border-bottom: 1px solid #a0a5a8;
            line-height: 2;
        }

        .title {
            font-size: 34px;
            font-weight: 700;
            line-height: 3;
            color: #181818;
            letter-spacing: 10px;
        }

        .description {
            font-size: 14px;
            letter-spacing: 0.25px;
            text-align: center;
            line-height: 1.6;
        }

        .button {
            width: 180px;
            height: 50px;
            border-radius: 25px;
            margin-top: 50px;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 1.15px;
            background-color: #4B70E2;
            color: #f9f9f9;
            box-shadow: 8px 8px 16px #d1d9e6, -8px -8px 16px #f9f9f9;
            border: none;
            outline: none;
        }

        .a-container {
            z-index: 100;
            left: calc(100% - 600px);
        }

        .b-container {
            left: calc(100% - 600px);
            z-index: 0;
        }

        .switch {
            display: flex;
            justify-content: center;
            align-items: center;
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 400px;
            padding: 50px;
            z-index: 200;
            transition: 1.25s;
            background-color: #ecf0f3;
            overflow: hidden;
            box-shadow: 4px 4px 10px #d1d9e6, -4px -4px 10px #d1d9e6;
        }

        .switch_circle {
            position: absolute;
            width: 500px;
            height: 500px;
            border-radius: 50%;
            background-color: #ecf0f3;
            box-shadow: inset 8px 8px 12px #b8bec7, inset -8px -8px 12px #fff;
            bottom: -60%;
            left: -60%;
            transition: 1.25s;
        }

        .switch_circle-t {
            top: -30%;
            left: 60%;
            width: 300px;
            height: 300px;
        }

        .switch_container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            position: absolute;
            width: 400px;
            padding: 50px 55px;
            transition: 1.25s;
        }

        .switch_button {
            cursor: pointer;
        }

        .switch_button:hover,
        .submit:hover {
            box-shadow: 6px 6px 10px #d1d9e6, -6px -6px 10px #f9f9f9;
            transform: scale(0.985);
            transition: 0.25s;
        }

        .switch_button:active,
        .switch_button:focus {
            box-shadow: 2px 2px 6px #d1d9e6, -2px -2px 6px #f9f9f9;
            transform: scale(0.97);
            transition: 0.25s;
        }

        .is-txr {
            left: calc(100% - 400px);
            transition: 1.25s;
            transform-origin: left;
        }

        .is-txl {
            left: 0;
            transition: 1.25s;
            transform-origin: right;
        }

        .is-z {
            z-index: 200;
            transition: 1.25s;
        }

        .is-hidden {
            visibility: hidden;
            opacity: 0;
            position: absolute;
            transition: 1.25s;
        }

        .is-gx {
            animation: is-gx 1.25s;
        }

        @keyframes is-gx {

            0%,
            10%,
            100% {
                width: 400px;
            }

            30%,
            50% {
                width: 500px;
            }
        }
</style>
