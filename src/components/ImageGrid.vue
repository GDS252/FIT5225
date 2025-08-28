<template>
  <div class="image-grid">
    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
      <p class="mt-3 text-muted">正在加载图片...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="images.length === 0" class="empty-state text-center py-5">
      <i class="bi bi-images display-1 text-muted mb-3"></i>
      <h4 class="text-muted">{{ emptyMessage }}</h4>
      <p class="text-muted">{{ emptySubMessage }}</p>
      <router-link v-if="showUploadButton" to="/upload" class="btn btn-primary">
        <i class="bi bi-cloud-upload me-2"></i>
        上传第一张图片
      </router-link>
    </div>

    <!-- 图片网格 -->
    <div v-else class="row g-4">
      <div
        v-for="image in images"
        :key="image.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <div class="card image-card h-100 shadow-sm">
          <!-- 图片 -->
          <div class="image-container position-relative">
            <img
              :src="image.thumbnailUrl || image.url"
              :alt="image.filename"
              class="card-img-top"
              @click="openImageModal(image)"
              style="cursor: pointer"
            />
            <div class="image-overlay">
              <button
                class="btn btn-light btn-sm me-2"
                @click="openImageModal(image)"
                title="查看大图"
              >
                <i class="bi bi-eye"></i>
              </button>
              <button
                class="btn btn-primary btn-sm me-2"
                @click="openTagModal(image)"
                title="编辑标签"
              >
                <i class="bi bi-tags"></i>
              </button>
              <button
                class="btn btn-danger btn-sm"
                @click="confirmDelete(image)"
                title="删除"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>

          <!-- 图片信息 -->
          <div class="card-body">
            <h6 class="card-title text-truncate" :title="image.filename">
              {{ image.filename }}
            </h6>
            
            <!-- 识别结果 -->
            <div v-if="image.predictions && image.predictions.length > 0" class="mb-2">
              <span class="badge bg-success me-1">
                {{ image.predictions[0].label }}
              </span>
              <small class="text-muted">
                {{ Math.round(image.predictions[0].confidence * 100) }}%
              </small>
            </div>

            <!-- 标签 -->
            <div v-if="image.tags && image.tags.length > 0" class="mb-2">
              <span
                v-for="tag in image.tags.slice(0, 3)"
                :key="tag"
                class="badge bg-secondary me-1 mb-1"
              >
                {{ tag }}
              </span>
              <span v-if="image.tags.length > 3" class="text-muted small">
                +{{ image.tags.length - 3 }} 更多
              </span>
            </div>

            <!-- 上传时间 -->
            <small class="text-muted">
              <i class="bi bi-clock me-1"></i>
              {{ formatDate(image.uploadedAt) }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片查看模态框 -->
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
            
            <!-- 详细信息 -->
            <div v-if="selectedImage" class="mt-3 text-start">
              <h6>识别结果：</h6>
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
              <p v-else class="text-muted">暂无识别结果</p>

              <h6 class="mt-3">标签：</h6>
              <div v-if="selectedImage.tags && selectedImage.tags.length > 0">
                <span
                  v-for="tag in selectedImage.tags"
                  :key="tag"
                  class="badge bg-secondary me-1 mb-1"
                >
                  {{ tag }}
                </span>
              </div>
              <p v-else class="text-muted">暂无标签</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑标签模态框 -->
    <div
      class="modal fade"
      id="tagModal"
      tabindex="-1"
      ref="tagModal"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">编辑标签</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label for="tagInput" class="form-label">标签（用逗号分隔）</label>
              <textarea
                id="tagInput"
                class="form-control"
                rows="3"
                v-model="tagInput"
                placeholder="例如：红色鸟类, 小型鸟, 花园鸟"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              取消
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="updateTags"
              :disabled="updatingTags"
            >
              <span v-if="updatingTags" class="spinner-border spinner-border-sm me-2"></span>
              保存
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'

export default {
  name: 'ImageGrid',
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
      default: '暂无图片'
    },
    emptySubMessage: {
      type: String,
      default: '上传一些图片来开始识别鸟类吧！'
    },
    showUploadButton: {
      type: Boolean,
      default: true
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
      if (confirm(`确定要删除 "${image.filename}" 吗？此操作无法撤销。`)) {
        this.$emit('delete-image', image.id)
      }
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
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
</style>
