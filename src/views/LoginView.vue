<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>User Login</h2>
      </template>
      
      <!-- Error Message -->
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        :closable="false"
        class="error-alert"
      />
      
      <!-- Success Message -->
      <el-alert
        v-if="successMessage"
        :title="successMessage"
        type="success"
        :closable="false"
        class="success-alert"
      />
      
      <el-form @submit.prevent="handleLogin" :model="formData" :rules="rules" ref="loginForm">
        <el-form-item label="Email" prop="email">
          <el-input 
            v-model="formData.email" 
            placeholder="Please enter your email" 
            size="large"
            type="email"
            :prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input 
            v-model="formData.password" 
            type="password" 
            placeholder="Please enter your password" 
            size="large" 
            show-password
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            native-type="submit" 
            style="width: 100%;" 
            size="large"
            :loading="isLoading"
            :disabled="isLoading"
          >
            {{ isLoading ? 'Logging in...' : 'Login' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="links">
        <router-link to="/register">Don't have an account? Register now</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { signIn } from 'aws-amplify/auth';
import { ElMessage } from 'element-plus';
import { Message, Lock } from '@element-plus/icons-vue';

// Form data
const formData = reactive({
  email: '',
  password: ''
});

// Form validation rules
const rules = reactive({
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 8, message: 'Password must be at least 8 characters', trigger: 'blur' }
  ]
});

const loginForm = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Get router instance for page navigation
const router = useRouter();

const handleLogin = async () => {
  // Validate form
  if (!loginForm.value) return;
  
  try {
    const valid = await loginForm.value.validate();
    if (!valid) return;
  } catch (error) {
    console.log('Form validation failed');
    return;
  }

  // Clear previous messages
  errorMessage.value = '';
  successMessage.value = '';
  isLoading.value = true;

  try {
    console.log('Attempting to login with AWS Cognito');

    // AWS Cognito authentication
    const { isSignedIn, nextStep } = await signIn({ 
      username: formData.email, 
      password: formData.password 
    });

    if (isSignedIn) {
      successMessage.value = 'Login successful! Redirecting to dashboard...';
      ElMessage.success('Welcome back!');
      console.log('Login successful');
      
      // Clear form data for security
      formData.email = '';
      formData.password = '';
      
      setTimeout(() => {
        router.push('/');
      }, 1000);
    } else {
      // Handle additional steps (e.g., MFA, password reset)
      console.log('Additional authentication step required:', nextStep);
      
      if (nextStep.signInStep === 'CONFIRM_SIGN_UP') {
        errorMessage.value = 'Please verify your email address first. Check your email for verification code.';
        ElMessage.warning('Account verification required');
        setTimeout(() => {
          router.push('/register');
        }, 2000);
      } else if (nextStep.signInStep === 'CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED') {
        errorMessage.value = 'Please set a new password for your account.';
      } else {
        errorMessage.value = `Additional authentication step required: ${nextStep.signInStep}`;
      }
    }

  } catch (error) {
    console.error('Login error:', error);
    errorMessage.value = getErrorMessage(error);
    ElMessage.error('Login failed');
    
    // Clear password field on error for security
    formData.password = '';
  } finally {
    isLoading.value = false;
  }
};

const getErrorMessage = (error) => {
  switch (error.name) {
    case 'NotAuthorizedException':
      return 'Invalid email or password. Please check your credentials and try again.';
    case 'UserNotFoundException':
      return 'Account not found. Please check your email or create a new account.';
    case 'UserNotConfirmedException':
      return 'Please verify your email address first. Check your email for verification code.';
    case 'TooManyRequestsException':
      return 'Too many failed attempts. Please wait a few minutes before trying again.';
    case 'InvalidParameterException':
      return 'Invalid input. Please check your email and password format.';
    case 'NetworkError':
      return 'Network error. Please check your internet connection and try again.';
    case 'PasswordResetRequiredException':
      return 'Password reset required. Please contact support or reset your password.';
    case 'UserNotConfirmedException':
      return 'Account not verified. Please check your email for verification instructions.';
    default:
      return error.message || 'Login failed. Please try again or contact support if the problem persists.';
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  border: none;
}

.login-card :deep(.el-card__header) {
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  margin: -1px -1px 0 -1px;
  padding: 24px;
}

.login-card :deep(.el-card__header) h2 {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
}

.login-card :deep(.el-card__body) {
  padding: 32px;
}

.error-alert {
  margin-bottom: 24px;
}

.success-alert {
  margin-bottom: 24px;
}

.el-form-item {
  margin-bottom: 24px;
}

.el-form-item :deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.el-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6;
  transition: all 0.3s ease;
}

.el-input :deep(.el-input__wrapper):hover {
  box-shadow: 0 0 0 1px #c0c4cc;
}

.el-input.is-focus :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #667eea;
}

.links {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.links a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  transition: color 0.3s ease;
}

.links a:hover {
  color: #5a67d8;
  text-decoration: underline;
}

.el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.el-button--primary:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .login-container {
    padding: 10px;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .login-card :deep(.el-card__body) {
    padding: 24px;
  }
}
</style>