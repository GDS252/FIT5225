<template>
  <div class="image-grid">
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading images...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="images.length === 0" class="empty-state text-center py-5">
      <i class="bi bi-images display-1 text-muted mb-3"></i>
      <h4 class="text-muted">{{ emptyMessage }}</h4>
      <p class="text-muted">{{ emptySubMessage }}</p>
      <router-link v-if="showUploadButton" to="/upload" class="btn btn-primary">
        <i class="bi bi-cloud-upload me-2"></i>
        Upload First Image
      </router-link>
    </div>

    <!-- Bulk Selection Info -->
    <div v-if="bulkSelectMode" class="bulk-selection-info mb-3">
      <div class="alert alert-info d-flex align-items-center">
        <i class="bi bi-check2-square me-2"></i>
        <span>{{ selectedImages.length }} image(s) selected for bulk operations</span>
      </div>
    </div>

    <!-- Image grid -->
    <div v-else class="row g-4">
      <div class="col-12 mb-3" v-if="!bulkMode">
        <button
          class="btn btn-outline-primary btn-sm"
          @click="toggleBulkMode"
        >
          <i class="bi bi-check2-square me-1"></i>
          Enable Bulk Selection
        </button>
      </div>
      
      <div
        v-for="image in images"
        :key="image.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <div 
          class="card image-card h-100 shadow-sm"
          :class="{ 'selected': isImageSelected(image), 'bulk-mode': bulkSelectMode }"
        >
          <!-- Bulk Selection Checkbox -->
          <div v-if="bulkSelectMode" class="bulk-checkbox">
            <input
              type="checkbox"
              class="form-check-input"
              :checked="isImageSelected(image)"
              @change="toggleSelection(image)"
            />
          </div>
          
          <!-- Image -->
          <div class="image-container position-relative">
            <img
              :src="image.thumbnailUrl || image.url"
              :alt="image.filename"
              class="card-img-top"
              @click="bulkSelectMode ? toggleSelection(image) : openImageModal(image)"
              style="cursor: pointer"
            />
            <div class="image-overlay" v-if="!bulkSelectMode">
              <button
                class="btn btn-light btn-sm me-2"
                @click="openImageModal(image)"
                title="View large image"
              >
                <i class="bi bi-eye"></i>
              </button>
              <button
                class="btn btn-primary btn-sm me-2"
                @click="openTagModal(image)"
                title="Edit tags"
              >
                <i class="bi bi-tags"></i>
              </button>
              <button
                class="btn btn-danger btn-sm"
                @click="confirmDelete(image)"
                title="Delete"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>

          <!-- Image information -->
          <div class="card-body">
            <h6 class="card-title text-truncate" :title="image.filename">
              {{ image.filename }}
            </h6>
            
            <!-- Recognition results -->
            <div v-if="image.predictions && image.predictions.length > 0" class="mb-2">
              <span class="badge bg-success me-1">
                {{ image.predictions[0].label }}
              </span>
              <small class="text-muted">
                {{ Math.round(image.predictions[0].confidence * 100) }}%
              </small>
            </div>

            <!-- Tags -->
            <div v-if="image.tags && image.tags.length > 0" class="mb-2">
              <span
                v-for="tag in image.tags.slice(0, 3)"
                :key="tag"
                class="badge bg-secondary me-1 mb-1"
              >
                {{ tag }}
              </span>
              <span v-if="image.tags.length > 3" class="text-muted small">
                +{{ image.tags.length - 3 }} more
              </span>
            </div>

            <!-- Upload time -->
            <small class="text-muted">
              <i class="bi bi-clock me-1"></i>
              {{ formatDate(image.uploadedAt) }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- Image view modal -->
    <div
      class="modal fade"
      id="imageModal"
      tabindex="-1"
      ref="imageModal"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedImage?.filename }}</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
            ></button>
          </div>
          <div class="modal-body text-center">
            <img
              v-if="selectedImage"
              :src="selectedImage.url"
              :alt="selectedImage.filename"
              class="img-fluid rounded"
            />
            
            <!-- Detailed information -->
            <div v-if="selectedImage" class="mt-3 text-start">
              <h6>Recognition Results:</h6>
              <div v-if="selectedImage.description">
                <p class="mb-2">{{ selectedImage.description }}</p>
              </div>
              <div v-if="selectedImage.predictions && selectedImage.predictions.length > 0">
                <div
                  v-for="(prediction, index) in selectedImage.predictions"
                  :key="index"
                  class="d-flex justify-content-between align-items-center mb-2"
                >
                  <span>{{ prediction.label }}</span>
                  <span class="badge bg-primary">
                    {{ Math.round(prediction.confidence * 100) }}%
                  </span>
                </div>
              </div>
              <p v-else-if="!selectedImage.description" class="text-muted">No recognition results available</p>

              <h6 class="mt-3">Tags:</h6>
              <div v-if="selectedImage.tags && selectedImage.tags.length > 0">
                <span
                  v-for="tag in selectedImage.tags"
                  :key="tag"
                  class="badge bg-secondary me-1 mb-1"
                >
                  {{ tag }}
                </span>
              </div>
              <p v-else class="text-muted">No tags available</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit tags modal -->
    <div
      class="modal fade"
      id="tagModal"
      tabindex="-1"
      ref="tagModal"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Tags</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label for="tagInput" class="form-label">Tags (separated by commas)</label>
              <textarea
                id="tagInput"
                class="form-control"
                rows="3"
                v-model="tagInput"
                placeholder="Example: red bird, small bird, garden bird"
              ></textarea>
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
              class="btn btn-primary"
              @click="updateTags"
              :disabled="updatingTags"
            >
              <span v-if="updatingTags" class="spinner-border spinner-border-sm me-2"></span>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Tag Manager Component -->

  </div>
</template>

<script>
import { Modal } from 'bootstrap'

export default {
  name: 'ImageGrid',
  components: {
  },
  props: {
    images: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    emptyMessage: {
      type: String,
      default: 'No images'
    },
    emptySubMessage: {
      type: String,
      default: 'Upload some images to start recognizing birds!'
    },
    showUploadButton: {
      type: Boolean,
      default: true
    },
    bulkSelectMode: {
      type: Boolean,
      default: false
    },
    selectedImages: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedImage: null,
      tagInput: '',
      updatingTags: false,
      imageModal: null,
      tagModal: null
    }
  },
  computed: {
  },
  mounted() {
    this.imageModal = new Modal(this.$refs.imageModal)
    this.tagModal = new Modal(this.$refs.tagModal)
  },
  methods: {
    openImageModal(image) {
      this.selectedImage = image
      this.imageModal.show()
    },
    openTagModal(image) {
      this.selectedImage = image
      this.tagInput = image.tags ? image.tags.join(', ') : ''
      this.tagModal.show()
    },
    async updateTags() {
      if (!this.selectedImage) return

      this.updatingTags = true
      try {
        const tags = this.tagInput
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag.length > 0)

        await this.$emit('update-tags', this.selectedImage.id, tags)
        this.tagModal.hide()
      } catch (error) {
        console.error('Error updating tags:', error)
      } finally {
        this.updatingTags = false
      }
    },
    confirmDelete(image) {
      if (confirm(`Are you sure you want to delete "${image.filename}"? This action cannot be undone.`)) {
        this.$emit('delete-image', image.id)
      }
    },
    
    // Bulk selection methods
    isImageSelected(image) {
      return this.selectedImages.some(img => img.id === image.id);
    },
    
    toggleSelection(image) {
      this.$emit('toggle-selection', image);
    },
    

    
    async handleBulkTagUpdate(operation) {
      try {
        console.log('Bulk tag operation:', operation);
        
        // Here we would normally call the API
        // For now, we'll emit to parent component
        this.$emit('bulk-tag-update', operation);
        
        // Clear selection after successful operation
        this.clearSelection();
        this.bulkMode = false;
        
      } catch (error) {
        console.error('Bulk tag update failed:', error);
        throw error; // Re-throw for component to handle
      }
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.image-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: none;
}

.image-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.image-container {
  overflow: hidden;
  height: 200px;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-container:hover img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-container:hover .image-overlay {
  opacity: 1;
}

.empty-state {
  padding: 4rem 2rem;
}

.badge {
  font-size: 0.75em;
}

.modal-body img {
  max-height: 70vh;
  object-fit: contain;
}

@media (max-width: 576px) {
  .image-container {
    height: 150px;
  }
  
  .image-overlay .btn {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
  }
}

/* Bulk selection styles */
.bulk-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 4px;
}

.image-card.bulk-mode {
  cursor: pointer;
  transition: all 0.2s ease;
}

.image-card.bulk-mode:hover {
  transform: translateY(-2px);
}

.image-card.selected {
  border: 3px solid #007bff !important;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25) !important;
}

.bulk-operations .alert {
  border: none;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
}
</style>
