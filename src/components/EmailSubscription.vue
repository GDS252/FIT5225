<template>
  <div class="email-subscription-footer bg-dark text-white py-4 mt-5">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-md-8">
          <div class="row align-items-center">
            <div class="col-md-6">
              <h5 class="mb-1">
                <i class="bi bi-envelope me-2"></i>
                Stay Updated!
              </h5>
              <p class="mb-0 text-muted">Subscribe to get notified when new bird images are tagged</p>
            </div>
            <div class="col-md-6">
              <div class="input-group">
                <input
                  type="email"
                  class="form-control"
                  v-model="subscriptionEmail"
                  placeholder="Enter your email address"
                  :disabled="subscribing"
                  @keyup.enter="subscribe"
                />
                <button
                  class="btn btn-primary"
                  type="button"
                  @click="subscribe"
                  :disabled="subscribing || !isValidEmail"
                >
                  <span v-if="subscribing" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-bell me-1"></i>
                  {{ subscribing ? 'Subscribing...' : 'Subscribe' }}
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4 text-md-end mt-3 mt-md-0">
          <div class="d-flex justify-content-md-end justify-content-center">
            <a href="#" class="text-white-50 me-3" title="GitHub">
              <i class="bi bi-github fs-4"></i>
            </a>
            <a href="#" class="text-white-50 me-3" title="Documentation">
              <i class="bi bi-book fs-4"></i>
            </a>
            <a href="#" class="text-white-50" title="Support">
              <i class="bi bi-question-circle fs-4"></i>
            </a>
          </div>
          <small class="text-muted mt-2 d-block">
            © 2024 Bird Recognition System
          </small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/axios.js';

export default {
  name: 'EmailSubscription',
  setup() {
    const subscriptionEmail = ref('');
    const subscribing = ref(false);

    const isValidEmail = computed(() => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(subscriptionEmail.value);
    });

    const subscribe = async () => {
      console.log('🔔 [EmailSubscription] Starting subscription process');
      console.log('📧 [EmailSubscription] Email to subscribe:', subscriptionEmail.value);
      
      if (!isValidEmail.value) {
        console.warn('⚠️ [EmailSubscription] Invalid email format:', subscriptionEmail.value);
        ElMessage.warning('Please enter a valid email address');
        return;
      }

      subscribing.value = true;
      console.log('🚀 [EmailSubscription] Sending subscription request to /subscribe');
      
      try {
        const requestPayload = {
          email: subscriptionEmail.value
        };
        console.log('📤 [EmailSubscription] Request payload:', requestPayload);
        
        const response = await apiClient.post('/subscribe', requestPayload);
        
        console.log('✅ [EmailSubscription] Subscription response received:', response);
        console.log('📊 [EmailSubscription] Response status:', response.status);
        console.log('📄 [EmailSubscription] Response data:', response.data);

        if (response.data) {
          console.log('🎉 [EmailSubscription] Subscription successful');
          ElMessage.success('Subscription successful! Please check your email to confirm.');
          subscriptionEmail.value = ''; // Clear the input
        }
      } catch (error) {
        console.error('❌ [EmailSubscription] Subscription error:', error);
        console.error('🔍 [EmailSubscription] Error details:', {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          config: {
            url: error.config?.url,
            method: error.config?.method,
            headers: error.config?.headers
          }
        });
        
        if (error.response?.status === 400) {
          console.warn('⚠️ [EmailSubscription] Bad request - invalid email');
          ElMessage.error('Invalid email address. Please try again.');
        } else if (error.response?.status === 500) {
          console.error('💥 [EmailSubscription] Server error');
          ElMessage.error('Subscription service error. Please try again later.');
        } else if (!error.response) {
          console.error('🌐 [EmailSubscription] Network error - no response received');
          ElMessage.error('Network error. Please check your connection and try again.');
        } else {
          console.error('🚫 [EmailSubscription] Unknown error occurred');
          ElMessage.error('Failed to subscribe. Please try again.');
        }
      } finally {
        subscribing.value = false;
        console.log('🏁 [EmailSubscription] Subscription process completed');
      }
    };

    return {
      subscriptionEmail,
      subscribing,
      isValidEmail,
      subscribe
    };
  }
};
</script>

<style scoped>
.email-subscription-footer {
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.input-group .form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  border-left: none;
}

.text-white-50:hover {
  color: white !important;
  transition: color 0.2s ease;
}
</style>
