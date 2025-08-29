import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// Bootstrap CSS (keep for some styles)
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

// AWS Amplify
import { Amplify } from 'aws-amplify';

// !!IMPORTANT!! Please replace the following values with your own Cognito User Pool information
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'ap-southeast-2_YLmR39QZq',         // Example: 'ap-southeast-2_xxxxxxxxx'
      userPoolClientId: '4erh8862poahob6rajh7qossc6', // Your App Client ID created in Cognito
      region:         'ap-southeast-2',
      loginWith: {
        email: true,
        username: false
      },
      signUpVerificationMethod: 'code',
      userAttributes: {
        email: {
          required: true
        }
      },
      allowGuestAccess: false,
      passwordFormat: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireNumbers: true,
        requireSpecialCharacters: true
      }
    }
  }
});

const app = createApp(App)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')
