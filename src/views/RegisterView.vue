<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>Create Account</h2>
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

      <!-- Registration form -->
      <el-form v-if="!showConfirmation" @submit.prevent="handleRegister" :model="formData" :rules="rules" ref="registerForm">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="First Name" prop="firstName">
              <el-input 
                v-model="formData.firstName" 
                placeholder="Enter first name" 
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Last Name" prop="lastName">
              <el-input 
                v-model="formData.lastName" 
                placeholder="Enter last name" 
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="Email Address" prop="email">
          <el-input 
            v-model="formData.email" 
            placeholder="Enter your email address" 
            size="large"
            type="email"
            :prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input 
            v-model="formData.password" 
            type="password" 
            placeholder="Create a strong password" 
            size="large" 
            show-password
            :prefix-icon="Lock"
          />
          <div class="password-requirements">
            <small class="text-muted">
              Password must contain at least 8 characters with uppercase, lowercase, numbers and special characters
            </small>
          </div>
        </el-form-item>
        
        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input 
            v-model="formData.confirmPassword" 
            type="password" 
            placeholder="Confirm your password" 
            size="large" 
            show-password
            :prefix-icon="Lock"
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <!-- Terms and Conditions -->
        <el-form-item prop="acceptTerms">
          <el-checkbox v-model="formData.acceptTerms" size="large">
            I agree to the <a href="#" class="terms-link">Terms of Service</a> and <a href="#" class="terms-link">Privacy Policy</a>
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleRegister" 
            native-type="submit" 
            style="width: 100%;" 
            size="large"
            :disabled="isLoading || !formData.acceptTerms"
            :loading="isLoading"
          >
            {{ isLoading ? 'Creating Account...' : 'Create Account' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Verification code confirmation form -->
      <el-form v-if="showConfirmation" @submit.prevent="handleConfirmSignUp" :model="confirmData" :rules="confirmRules" ref="confirmForm">
        <div class="verification-header">
          <el-icon class="verification-icon"><SuccessFilled /></el-icon>
          <h3>Check Your Email</h3>
          <p class="verification-text">
            We've sent a verification code to <strong>{{ formData.email }}</strong>
          </p>
        </div>
        
        <el-form-item label="Verification Code" prop="confirmationCode">
          <el-input 
            v-model="confirmData.confirmationCode" 
            placeholder="Enter 6-digit verification code" 
            size="large"
            maxlength="6"
            :prefix-icon="Key"
            @keyup.enter="handleConfirmSignUp"
          />
          <div class="form-text">
            Please check your email inbox and spam folder for the verification code
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleConfirmSignUp" 
            native-type="submit" 
            style="width: 100%;" 
            size="large"
            :loading="isLoading"
          >
            {{ isLoading ? 'Verifying...' : 'Verify Email' }}
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="default" 
            @click="resendConfirmationCode" 
            style="width: 100%;" 
            size="large"
            :disabled="isLoading || resendCooldown > 0"
          >
            {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Code' }}
          </el-button>
        </el-form-item>
        
        <div class="verification-help">
          <p class="text-muted">
            <el-icon><InfoFilled /></el-icon>
            Didn't receive the code? Check your spam folder or try resending
          </p>
        </div>
      </el-form>
      
      <div class="links">
        <router-link to="/login">Already have an account? Sign in</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { signUp, confirmSignUp, resendSignUpCode } from 'aws-amplify/auth';
import { ElMessage } from 'element-plus';
import { User, Message, Lock, Key, SuccessFilled, InfoFilled } from '@element-plus/icons-vue';

// Form data
const formData = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
});

const confirmData = reactive({
  confirmationCode: ''
});

// Form validation rules
const rules = reactive({
  firstName: [
    { required: true, message: 'Please enter your first name', trigger: 'blur' },
    { min: 2, message: 'First name must be at least 2 characters', trigger: 'blur' }
  ],
  lastName: [
    { required: true, message: 'Please enter your last name', trigger: 'blur' },
    { min: 2, message: 'Last name must be at least 2 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter your email address', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please create a password', trigger: 'blur' },
    { min: 8, message: 'Password must be at least 8 characters', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (!value) {
          callback();
          return;
        }
        
        const hasUpper = /[A-Z]/.test(value);
        const hasLower = /[a-z]/.test(value);
        const hasNumber = /\d/.test(value);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
        
        if (!hasUpper || !hasLower || !hasNumber || !hasSpecial) {
          callback(new Error('Password must contain uppercase, lowercase, numbers and special characters'));
        } else {
          callback();
        }
      }, 
      trigger: 'blur' 
    }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your password', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== formData.password) {
          callback(new Error('Passwords do not match'));
        } else {
          callback();
        }
      }, 
      trigger: 'blur' 
    }
  ],
  acceptTerms: [
    { 
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('Please accept the terms of service'));
        } else {
          callback();
        }
      }, 
      trigger: 'change' 
    }
  ]
});

const confirmRules = reactive({
  confirmationCode: [
    { required: true, message: 'Please enter the verification code', trigger: 'blur' },
    { len: 6, message: 'Verification code must be 6 digits', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: 'Verification code must contain only numbers', trigger: 'blur' }
  ]
});

const registerForm = ref(null);
const confirmForm = ref(null);
const showConfirmation = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const resendCooldown = ref(0);

// Get router instance for page navigation
const router = useRouter();

const handleRegister = async () => {
  // Validate form
  if (!registerForm.value) return;
  
  try {
    const valid = await registerForm.value.validate();
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
    console.log('Attempting to register user with AWS Cognito');

    // AWS Cognito user registration
    const { isSignUpComplete, userId, nextStep } = await signUp({
      username: formData.email,
      password: formData.password,
      options: {
        userAttributes: {
          email: formData.email,
          given_name: formData.firstName,
          family_name: formData.lastName
        }
      }
    });

    if (isSignUpComplete) {
      successMessage.value = 'Account created successfully! You can now sign in.';
      ElMessage.success('Registration completed successfully!');
      
      // Clear sensitive data
      formData.password = '';
      formData.confirmPassword = '';
      
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } else if (nextStep.signUpStep === 'CONFIRM_SIGN_UP') {
      successMessage.value = 'Account created! Please verify your email address.';
      ElMessage.success('Please check your email for verification code');
      showConfirmation.value = true;
      console.log('User registered, verification required:', userId);
    }

  } catch (error) {
    console.error('Registration error:', error);
    errorMessage.value = getErrorMessage(error);
    ElMessage.error('Registration failed');
  } finally {
    isLoading.value = false;
  }
};

const handleConfirmSignUp = async () => {
  // Validate form
  if (!confirmForm.value) return;
  
  try {
    const valid = await confirmForm.value.validate();
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
    console.log('Confirming registration');

    // Confirm user registration with verification code
    const { isSignUpComplete, nextStep } = await confirmSignUp({
      username: formData.email,
      confirmationCode: confirmData.confirmationCode
    });

    if (isSignUpComplete) {
      successMessage.value = 'Email verified successfully! Redirecting to sign in page...';
      ElMessage.success('Account verified! You can now sign in.');
      
      // Clear all form data
      Object.keys(formData).forEach(key => {
        if (typeof formData[key] === 'string') {
          formData[key] = '';
        } else if (typeof formData[key] === 'boolean') {
          formData[key] = false;
        }
      });
      confirmData.confirmationCode = '';
      
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } else {
      console.log('Additional verification step required:', nextStep);
      errorMessage.value = 'Additional verification step required. Please try again.';
    }

  } catch (error) {
    console.error('Confirmation error:', error);
    errorMessage.value = getErrorMessage(error);
    ElMessage.error('Verification failed');
  } finally {
    isLoading.value = false;
  }
};

const resendConfirmationCode = async () => {
  if (resendCooldown.value > 0) return;
  
  isLoading.value = true;
  errorMessage.value = '';

  try {
    console.log('Resending verification code');

    await resendSignUpCode({
      username: formData.email
    });

    successMessage.value = 'Verification code has been resent to your email';
    ElMessage.success('Verification code resent successfully');
    
    // Start cooldown timer
    resendCooldown.value = 60;
    const timer = setInterval(() => {
      resendCooldown.value--;
      if (resendCooldown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);

  } catch (error) {
    console.error('Resend error:', error);
    errorMessage.value = getErrorMessage(error);
    ElMessage.error('Failed to resend verification code');
  } finally {
    isLoading.value = false;
  }
};

const getErrorMessage = (error) => {
  switch (error.name) {
    case 'UsernameExistsException':
      return 'An account with this email address already exists. Please sign in or use a different email.';
    case 'InvalidPasswordException':
      return 'Password does not meet security requirements. Please ensure it contains uppercase, lowercase, numbers and special characters.';
    case 'InvalidParameterException':
      return 'Invalid information provided. Please check all fields and try again.';
    case 'CodeMismatchException':
      return 'Invalid verification code. Please check the code and try again.';
    case 'ExpiredCodeException':
      return 'Verification code has expired. Please request a new code.';
    case 'TooManyRequestsException':
      return 'Too many attempts. Please wait a few minutes before trying again.';
    case 'NetworkError':
      return 'Network error. Please check your internet connection and try again.';
    case 'LimitExceededException':
      return 'Account creation limit reached. Please try again later or contact support.';
    default:
      return error.message || 'Registration failed. Please try again or contact support if the problem persists.';
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 520px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  border: none;
}

.register-card :deep(.el-card__header) {
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  margin: -1px -1px 0 -1px;
  padding: 24px;
}

.register-card :deep(.el-card__header) h2 {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
}

.register-card :deep(.el-card__body) {
  padding: 32px;
}

.el-form-item {
  margin-bottom: 20px;
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

.password-requirements {
  margin-top: 4px;
}

.password-requirements small {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.terms-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.terms-link:hover {
  text-decoration: underline;
}

.verification-header {
  text-align: center;
  margin-bottom: 24px;
}

.verification-icon {
  font-size: 48px;
  color: #67c23a;
  margin-bottom: 16px;
}

.verification-header h3 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.verification-text {
  color: #606266;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.form-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.verification-help {
  text-align: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.verification-help p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.error-alert {
  margin-bottom: 24px;
}

.success-alert {
  margin-bottom: 24px;
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

.el-button--primary:disabled {
  background: #c0c4cc;
  transform: none;
  box-shadow: none;
}

@media (max-width: 768px) {
  .register-container {
    padding: 10px;
  }
  
  .register-card {
    max-width: 100%;
  }
  
  .register-card :deep(.el-card__body) {
    padding: 24px;
  }
  
  .el-row .el-col {
    margin-bottom: 0;
  }
}
</style>