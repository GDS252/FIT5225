<template>
  <div class="bulk-tag-manager">
    <!-- Bulk Tag Management Modal -->
    <div
      class="modal fade"
      id="bulkTagModal"
      tabindex="-1"
      aria-labelledby="bulkTagModalLabel"
      aria-hidden="true"
      ref="bulkTagModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="bulkTagModalLabel">
              <i class="bi bi-tags me-2"></i>
              Bulk Tag Management
            </h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <!-- Selected Images Info -->
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              <strong>{{ selectedImages.length }}</strong> image(s) selected for tag management
            </div>

            <!-- Tag Operation Type -->
            <div class="mb-3">
              <label class="form-label fw-bold">Operation Type</label>
              <div class="btn-group w-100" role="group">
                <input
                  type="radio"
                  class="btn-check"
                  name="operation"
                  id="addTags"
                  value="add"
                  v-model="operation"
                />
                <label class="btn btn-outline-success" for="addTags">
                  <i class="bi bi-plus-circle me-1"></i>
                  Add Tags
                </label>

                <input
                  type="radio"
                  class="btn-check"
                  name="operation"
                  id="removeTags"
                  value="remove"
                  v-model="operation"
                />
                <label class="btn btn-outline-danger" for="removeTags">
                  <i class="bi bi-dash-circle me-1"></i>
                  Remove Tags
                </label>
              </div>
            </div>

            <!-- Tags Input -->
            <div class="mb-3">
              <label for="tagsInput" class="form-label fw-bold">
                Tags to {{ operation === 'add' ? 'Add' : 'Remove' }}
              </label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-tags"></i>
                </span>
                <input
                  type="text"
                  class="form-control"
                  id="tagsInput"
                  v-model="tagsInput"
                  :placeholder="operation === 'add' ? 'e.g. Peacock, 0.95; Crow, 0.8' : 'e.g. Peacock, Crow'"
                />
              </div>
              <div class="form-text">
                <template v-if="operation === 'add'">
                  Format: "TagName, Confidence" pairs separated by semicolons<br>
                  Example: "Peacock, 0.95; Crow, 0.8; Small Bird, 0.75"
                </template>
                <template v-else>
                  Format: Tag names separated by commas<br>
                  Example: "Peacock, Crow, Small Bird"
                </template>
              </div>
            </div>

            <!-- Preview Tags -->
            <div v-if="parsedTags.length > 0" class="mb-3">
              <label class="form-label fw-bold">Preview</label>
              <div class="d-flex flex-wrap gap-2">
                <span
                  v-for="tag in parsedTags"
                  :key="tag.name"
                  class="badge"
                  :class="operation === 'add' ? 'bg-success' : 'bg-danger'"
                >
                  {{ tag.name }}
                  <span v-if="operation === 'add' && tag.confidence !== undefined">
                    ({{ (tag.confidence * 100).toFixed(0) }}%)
                  </span>
                </span>
              </div>
            </div>

            <!-- Selected Images Preview -->
            <div class="mb-3">
              <label class="form-label fw-bold">Selected Images</label>
              <div class="row g-2" style="max-height: 200px; overflow-y: auto;">
                <div
                  v-for="image in selectedImages.slice(0, 6)"
                  :key="image.fileId"
                  class="col-md-2 col-4"
                >
                  <div class="card">
                    <img
                      :src="image.thumbnail_url || image.original_url"
                      class="card-img-top"
                      style="height: 60px; object-fit: cover;"
                      :alt="'Image ' + image.fileId"
                    />
                  </div>
                </div>
                <div v-if="selectedImages.length > 6" class="col-md-2 col-4">
                  <div class="card bg-light d-flex align-items-center justify-content-center" style="height: 80px;">
                    <span class="text-muted">+{{ selectedImages.length - 6 }} more</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn"
              :class="operation === 'add' ? 'btn-success' : 'btn-danger'"
              @click="performBulkTagUpdate"
              :disabled="updating || parsedTags.length === 0"
            >
              <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi" :class="operation === 'add' ? 'bi-plus-circle' : 'bi-dash-circle'"></i>
              {{ updating ? 'Updating...' : (operation === 'add' ? 'Add Tags' : 'Remove Tags') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api/axios.js';

export default {
  name: 'BulkTagManager',
  props: {
    selectedImages: {
      type: Array,
      default: () => []
    }
  },
  emits: ['tagsUpdated'],
  setup(props, { emit }) {
    const operation = ref('add'); // 'add' or 'remove'
    const tagsInput = ref('');
    const updating = ref(false);

    const parsedTags = computed(() => {
      if (!tagsInput.value.trim()) return [];
      
      if (operation.value === 'add') {
        // For add operation, expect "TagName, Confidence" pairs separated by semicolons or newlines
        // Example: "Peacock, 0.95; Crow, 0.8" or "Peacock, 0.95\nCrow, 0.8"
        const entries = tagsInput.value.split(/[;\n]/).map(entry => entry.trim()).filter(entry => entry);
        
        return entries.map(entry => {
          const parts = entry.split(',').map(p => p.trim());
          if (parts.length === 2) {
            const tagName = parts[0];
            const confidence = parseFloat(parts[1]);
            if (!isNaN(confidence) && confidence >= 0 && confidence <= 1) {
              return { name: tagName, confidence };
            }
          }
          // If no valid confidence, default to 0.8
          return { name: entry, confidence: 0.8 };
        });
      } else {
        // For remove operation, just tag names separated by commas
        const tags = tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag);
        return tags.map(tag => ({ name: tag }));
      }
    });

    // Clear tags input when operation changes
    watch(operation, () => {
      tagsInput.value = '';
    });

    const performBulkTagUpdate = async () => {
      console.log('🏷️ [BulkTagManager] Starting bulk tag update process');
      console.log('📊 [BulkTagManager] Selected images count:', props.selectedImages.length);
      console.log('🔧 [BulkTagManager] Operation type:', operation.value);
      console.log('📝 [BulkTagManager] Raw tags input:', tagsInput.value);
      console.log('🏷️ [BulkTagManager] Parsed tags:', parsedTags.value);
      
      if (props.selectedImages.length === 0) {
        console.warn('⚠️ [BulkTagManager] No images selected');
        ElMessage.warning('No images selected');
        return;
      }

      if (parsedTags.value.length === 0) {
        console.warn('⚠️ [BulkTagManager] No tags to process');
        ElMessage.warning('Please enter tags to ' + (operation.value === 'add' ? 'add' : 'remove'));
        return;
      }

      updating.value = true;
      console.log('🚀 [BulkTagManager] Processing bulk tag update...');
      
      try {
        // Prepare the request body
        const urls = props.selectedImages.map(image => image.original_url || image.url);
        console.log('🔗 [BulkTagManager] Image URLs to update:', urls);
        
        const tags = parsedTags.value.map(tag => {
          if (operation.value === 'add') {
            return `${tag.name}, ${tag.confidence}`;
          } else {
            return tag.name;
          }
        });
        console.log('🏷️ [BulkTagManager] Formatted tags for API:', tags);

        const requestBody = {
          urls: urls,
          operation: operation.value === 'add' ? 1 : 0, // 1 for add, 0 for remove
          tags: tags
        };

        console.log('📤 [BulkTagManager] Request body:', JSON.stringify(requestBody, null, 2));
        console.log('🎯 [BulkTagManager] Sending request to /tags/update');

        const response = await apiClient.post('/tags/update', requestBody);

        console.log('✅ [BulkTagManager] Bulk tag update response received:', response);
        console.log('📊 [BulkTagManager] Response status:', response.status);
        console.log('📄 [BulkTagManager] Response data:', response.data);

        if (response.data) {
          const actionText = operation.value === 'add' ? 'added to' : 'removed from';
          console.log(`🎉 [BulkTagManager] Tags successfully ${actionText} ${props.selectedImages.length} image(s)`);
          ElMessage.success(`Tags successfully ${actionText} ${props.selectedImages.length} image(s)`);
          
          // Clear form
          tagsInput.value = '';
          console.log('🧹 [BulkTagManager] Form cleared');
          
          // Close modal
          const modal = document.getElementById('bulkTagModal');
          const bsModal = bootstrap.Modal.getInstance(modal);
          if (bsModal) {
            bsModal.hide();
            console.log('🔒 [BulkTagManager] Modal closed');
          } else {
            console.warn('⚠️ [BulkTagManager] Could not find modal instance to close');
          }
          
          // Emit event to refresh data
          emit('tagsUpdated');
          console.log('📡 [BulkTagManager] tagsUpdated event emitted');
        }
      } catch (error) {
        console.error('❌ [BulkTagManager] Bulk tag update error:', error);
        console.error('🔍 [BulkTagManager] Error details:', {
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
          console.warn('⚠️ [BulkTagManager] Bad request - invalid format');
          ElMessage.error('Invalid request. Please check your input format.');
        } else if (error.response?.status === 500) {
          console.error('💥 [BulkTagManager] Server error');
          ElMessage.error('Server error. Please try again later.');
        } else if (!error.response) {
          console.error('🌐 [BulkTagManager] Network error - no response received');
          ElMessage.error('Network error. Please check your connection and try again.');
        } else {
          console.error('🚫 [BulkTagManager] Unknown error occurred');
          ElMessage.error('Failed to update tags. Please try again.');
        }
      } finally {
        updating.value = false;
        console.log('🏁 [BulkTagManager] Bulk tag update process completed');
      }
    };

    return {
      operation,
      tagsInput,
      updating,
      parsedTags,
      performBulkTagUpdate
    };
  }
};
</script>

<style scoped>
.badge {
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
}

.btn-check:checked + .btn {
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-btn-color), 0.25);
}

.modal-body {
  max-height: 70vh;
  overflow-y: auto;
}

.card-img-top {
  border-radius: 0.375rem;
}
</style>