<template>
  <div class="upload-page">
    <!-- Header Navigation -->
    <AppHeader />

    <!-- Main Content Area -->
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <!-- Page Title -->
          <div class="text-center mb-5">
            <h1 class="display-4 fw-bold text-primary mb-3">Upload Bird Images</h1>
            <p class="lead text-muted">Upload your bird photos and let AI identify the species</p>
          </div>

          <!-- Upload Component -->
          <div class="card upload-card shadow-lg border-0">
            <div class="card-body p-5">
              <UploadComponent 
                ref="uploadComponent"
                @upload-success="handleUploadSuccess"
                @upload-error="handleUploadError"
              />
            </div>
          </div>

          <!-- Upload Tips and Information -->
          <div class="row mt-5">
            <div class="col-md-6">
              <div class="info-card">
                <h5 class="text-primary mb-3">
                  <i class="bi bi-lightbulb me-2"></i>
                  Upload Tips
                </h5>
                <ul class="list-unstyled">
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Clear bird photos work better for identification
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Supports batch upload of multiple images
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    System will automatically identify bird species
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    You can add custom tags to images
                  </li>
                </ul>
              </div>
            </div>
            <div class="col-md-6">
              <div class="info-card">
                <h5 class="text-primary mb-3">
                  <i class="bi bi-info-circle me-2"></i>
                  Technical Details
                </h5>
                <div class="tech-details">
                  <div class="mb-3">
                    <strong>Supported Formats:</strong>
                    <div class="format-list mt-2">
                      <span class="badge bg-light text-dark me-2 mb-2">JPG</span>
                      <span class="badge bg-light text-dark me-2 mb-2">JPEG</span>
                      <span class="badge bg-light text-dark me-2 mb-2">PNG</span>
                      <span class="badge bg-light text-dark me-2 mb-2">GIF</span>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <strong>Upload Process:</strong>
                    <ol class="mt-2 small">
                      <li>Get presigned URL from backend</li>
                      <li>Upload directly to AWS S3</li>
                      <li>Trigger AI processing</li>
                      <li>Results available in dashboard</li>
                    </ol>
                  </div>
                  
                  <p class="text-muted mb-0">
                    <i class="bi bi-exclamation-triangle me-1"></i>
                    Maximum file size: 10MB per file
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Uploads -->
          <div v-if="recentUploads.length > 0" class="mt-5">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h4>
                <i class="bi bi-clock-history me-2"></i>
                Recent Uploads
              </h4>
              <button 
                class="btn btn-outline-primary btn-sm"
                @click="loadRecentUploads"
                :disabled="loadingRecent"
              >
                <span v-if="loadingRecent" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-arrow-clockwise me-1"></i>
                Refresh
              </button>
            </div>
            
            <div class="row g-3">
              <div
                v-for="upload in recentUploads"
                :key="upload.id"
                class="col-md-6 col-lg-4"
              >
                <div class="card recent-upload-card">
                  <img
                    :src="upload.thumbnailUrl || upload.url"
                    :alt="upload.filename"
                    class="card-img-top"
                  />
                  <div class="card-body">
                    <h6 class="card-title text-truncate" :title="upload.filename">
                      {{ upload.filename }}
                    </h6>
                    
                    <!-- AI Recognition Results -->
                    <div v-if="upload.predictions && upload.predictions.length > 0" class="mb-2">
                      <span 
                        v-for="(prediction, index) in upload.predictions.slice(0, 2)"
                        :key="index"
                        class="badge bg-success me-1 mb-1"
                      >
                        {{ prediction.label }} ({{ Math.round(prediction.confidence * 100) }}%)
                      </span>
                    </div>
                    
                    <!-- Custom Tags -->
                    <div v-if="upload.tags && upload.tags.length > 0" class="mb-2">
                      <span
                        v-for="tag in upload.tags.slice(0, 3)"
                        :key="tag"
                        class="badge bg-secondary me-1 mb-1"
                      >
                        {{ tag }}
                      </span>
                    </div>
                    
                    <small class="text-muted">
                      <i class="bi bi-calendar me-1"></i>
                      {{ formatDate(upload.uploadedAt) }}
                    </small>
                  </div>
                  
                  <!-- Quick Actions -->
                  <div class="card-footer bg-transparent">
                    <div class="btn-group w-100" role="group">
                      <button 
                        class="btn btn-outline-primary btn-sm"
                        @click="viewInDashboard(upload)"
                      >
                        <i class="bi bi-eye me-1"></i>
                        View
                      </button>
                      <button 
                        class="btn btn-outline-danger btn-sm"
                        @click="deleteUpload(upload)"
                      >
                        <i class="bi bi-trash me-1"></i>
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="text-center mt-5">
            <router-link to="/" class="btn btn-outline-primary btn-lg me-3">
              <i class="bi bi-arrow-left me-2"></i>
              Back to Dashboard
            </router-link>
            <button 
              class="btn btn-secondary btn-lg"
              @click="clearAllUploads"
            >
              <i class="bi bi-trash me-2"></i>
              Clear All
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import AppHeader from '../components/AppHeader.vue';
import UploadComponent from '../components/UploadComponent.vue';
import apiClient from '@/api/axios.js';

const router = useRouter();
const uploadComponent = ref(null);
const recentUploads = ref([]);
const loadingRecent = ref(false);

const handleUploadSuccess = (data) => {
  console.log('Upload successful:', data);
  ElMessage.success(`${data.file.name} uploaded successfully!`);
  
  // Refresh recent uploads to show the new file
  setTimeout(() => {
    loadRecentUploads();
  }, 2000);
};

const handleUploadError = (data) => {
  console.error('Upload failed:', data);
  ElMessage.error(`Failed to upload ${data.file.name}`);
};

const loadRecentUploads = async () => {
  loadingRecent.value = true;
  
  try {
    console.log('Loading recent uploads...');
    
    // Call backend API to get recent uploads
    const response = await apiClient.get('/files?limit=6&sort=recent');
    
    console.log('Recent uploads response:', response.data);
    console.log('Recent uploads response type:', typeof response.data);
    console.log('Recent uploads response structure:', JSON.stringify(response.data, null, 2));
    
    // Handle different response formats
    let files = [];
    if (response.data && response.data.files && Array.isArray(response.data.files)) {
      // Response format: { files: [...] }
      files = response.data.files;
    } else if (Array.isArray(response.data)) {
      // Response format: [...]
      files = response.data;
    } else if (response.data && typeof response.data === 'object') {
      // Response format: { data: [...] } or other object structure
      files = response.data.data || response.data.items || [];
    }
    
    console.log('Processed files array:', files);
    
    recentUploads.value = files.slice(0, 6).map(file => ({
      id: file.id || file.fileId || file.media_id || file.filename || Math.random().toString(36),
      filename: file.filename || file.name || file.originalName || 'unknown',
      url: file.original_url || file.url || file.fileUrl || '',
      thumbnailUrl: file.thumbnail_url || file.thumbnailUrl || file.thumbnail || file.original_url || '',
      uploadedAt: file.uploadedAt || file.createdAt || file.timestamp || new Date().toISOString(),
      predictions: file.predictions || file.aiResults || file.analysis || [],
      tags: file.tags || file.customTags || []
    }));
    
    console.log('Final recentUploads value:', recentUploads.value);
    
  } catch (error) {
    console.error('Error loading recent uploads:', error);
    console.error('Error details:', error.response?.data || error.message);
    
    // Only use mock data if there's a real API error, not data format issues
    if (error.response?.status === 404 || error.response?.status >= 500) {
      console.log('Using mock data due to API error');
      recentUploads.value = generateMockRecentUploads();
    } else {
      // For other errors (like 401, 403), just show empty list
      recentUploads.value = [];
    }
  } finally {
    loadingRecent.value = false;
  }
};

const viewInDashboard = (upload) => {
  // Navigate to dashboard and potentially filter by this file
  router.push({
    path: '/',
    query: { highlight: upload.id }
  });
};

const deleteUpload = async (upload) => {
  try {
    // Add detailed debugging to see what we have
    console.log('Object received by deleteUpload - full upload object:', upload);
    console.log('Available upload properties:', upload ? Object.keys(upload) : 'No upload found');
    
    // Check for URL in different possible property names
    const uploadUrl = (upload.url && upload.url.trim()) || 
                      (upload.original_url && upload.original_url.trim()) ||
                      (upload.s3_url && upload.s3_url.trim()) || 
                      (upload.fileUrl && upload.fileUrl.trim()) || 
                      (upload.src && upload.src.trim());
    console.log('Upload URL candidates:', {
      'upload.url': upload.url,
      'upload.original_url': upload.original_url,
      'upload.s3_url': upload.s3_url,
      'upload.fileUrl': upload.fileUrl,
      'upload.src': upload.src,
      'selected': uploadUrl
    });

    if (!uploadUrl) {
      ElMessage.error('Cannot find upload URL for deletion');
      console.error('No valid URL found in upload object:', upload);
      return;
    }

    await ElMessageBox.confirm(
      `Are you sure you want to delete "${upload.filename || upload.name || 'this file'}"?`,
      'Confirm Deletion',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    );

    console.log('Deleting upload:', upload.id, uploadUrl);
    
    // Extract filename from URL for backend API
    // Backend expects just the filename, not the full URL
    const filename = uploadUrl.split('/').pop();
    console.log('Extracted filename:', filename);
    
    // Call backend API to delete file
    console.log('Sending delete request with payload:', { urls: [filename] });
    await apiClient.post('/admin/files', {
      urls: [filename]
    });
    
    ElMessage.success('File deleted successfully');
    
    // Reload data from backend to get updated list
    console.log('Reloading recent uploads from backend after deletion...');
    await loadRecentUploads();
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Error deleting file:', error);
      ElMessage.error('Failed to delete file');
    }
  }
};

const clearAllUploads = () => {
  if (uploadComponent.value) {
    uploadComponent.value.clearFiles();
    ElMessage.info('Upload queue cleared');
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const generateMockRecentUploads = () => {
  return [
    {
      id: '1',
      filename: 'house_sparrow.jpg',
      url: 'https://via.placeholder.com/300x200/8BC34A/FFFFFF?text=House+Sparrow',
      thumbnailUrl: 'https://via.placeholder.com/150x100/8BC34A/FFFFFF?text=House+Sparrow',
      uploadedAt: new Date().toISOString(),
      predictions: [
        { label: 'House Sparrow', confidence: 0.94 },
        { label: 'Small Bird', confidence: 0.87 }
      ],
      tags: ['urban bird', 'common']
    },
    {
      id: '2',
      filename: 'american_robin.jpg',
      url: 'https://via.placeholder.com/300x200/FF9800/FFFFFF?text=American+Robin',
      thumbnailUrl: 'https://via.placeholder.com/150x100/FF9800/FFFFFF?text=American+Robin',
      uploadedAt: new Date(Date.now() - 3600000).toISOString(),
      predictions: [
        { label: 'American Robin', confidence: 0.89 }
      ],
      tags: ['red breast', 'garden bird']
    }
  ];
};

// Lifecycle
onMounted(() => {
  loadRecentUploads();
});
</script>

<style scoped>
.upload-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.upload-card {
  border-radius: 1rem;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.format-list .badge {
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
}

.tech-details .small {
  font-size: 0.875rem;
  color: #666;
}

.tech-details ol {
  padding-left: 1.25rem;
}

.recent-upload-card {
  border: none;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.recent-upload-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.recent-upload-card .card-img-top {
  height: 150px;
  object-fit: cover;
}

.recent-upload-card .card-body {
  padding: 1rem;
}

.recent-upload-card .card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.badge {
  font-size: 0.75rem;
}

.btn-group .btn {
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .upload-card .card-body {
    padding: 2rem 1rem;
  }
  
  .info-card {
    margin-bottom: 1rem;
  }
  
  .recent-upload-card .card-img-top {
    height: 120px;
  }
  
  .btn-group .btn {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
  }
}
</style>