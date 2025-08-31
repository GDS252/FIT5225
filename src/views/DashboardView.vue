<template>
  <div class="dashboard">
    <!-- Header Navigation -->
    <AppHeader />

    <!-- Main Content Area -->
    <div class="container-fluid py-4">
      <!-- Welcome Section and Statistics -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="welcome-section bg-gradient text-white rounded-3 p-4 mb-4">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h2 class="mb-2">Welcome Back!</h2>
                <p class="mb-0 opacity-75">Explore your bird recognition collection</p>
              </div>
              <div class="col-md-4 text-md-end">
                <router-link to="/upload" class="btn btn-light btn-lg">
                  <i class="bi bi-cloud-upload me-2"></i>
                  Upload New Images
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card stats-card h-100">
            <div class="card-body text-center">
              <i class="bi bi-images display-4 text-primary mb-2"></i>
              <h4 class="card-title">{{ totalImages }}</h4>
              <p class="card-text text-muted">Total Images</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card stats-card h-100">
            <div class="card-body text-center">
              <i class="bi bi-check-circle display-4 text-success mb-2"></i>
              <h4 class="card-title">{{ identifiedImages }}</h4>
              <p class="card-text text-muted">Identified</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card stats-card h-100">
            <div class="card-body text-center">
              <i class="bi bi-tags display-4 text-info mb-2"></i>
              <h4 class="card-title">{{ totalTags }}</h4>
              <p class="card-text text-muted">Total Tags</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card stats-card h-100">
            <div class="card-body text-center">
              <i class="bi bi-calendar-week display-4 text-warning mb-2"></i>
              <h4 class="card-title">{{ thisWeekUploads }}</h4>
              <p class="card-text text-muted">This Week</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Search and Filter Area -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card search-card">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-search me-2"></i>
                Search and Filter
              </h5>
              
              <form @submit.prevent="performSearch">
                <div class="row g-3">
                  <!-- Bird Tags Search -->
                  <div class="col-md-6">
                    <label for="birdTags" class="form-label">Bird Tags Query</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-tags"></i>
                      </span>
                      <input
                        type="text"
                        class="form-control"
                        id="birdTags"
                        v-model="searchForm.tags"
                        placeholder="e.g. crow, sparrow, eagle..."
                      />
                    </div>
                  </div>

                  <!-- Confidence Threshold -->
                  <div class="col-md-3">
                    <label for="confidence" class="form-label">Min Confidence</label>
                    <div class="input-group">
                      <span class="input-group-text">%</span>
                      <input
                        type="number"
                        class="form-control"
                        id="confidence"
                        v-model="searchForm.confidence"
                        min="0"
                        max="100"
                        step="5"
                        placeholder="50"
                      />
                    </div>
                  </div>

                  <!-- Search Button -->
                  <div class="col-md-3">
                    <label class="form-label">&nbsp;</label>
                    <div class="d-grid gap-2">
                      <button
                        type="submit"
                        class="btn btn-primary"
                        :disabled="searchLoading"
                      >
                        <span v-if="searchLoading" class="spinner-border spinner-border-sm me-2"></span>
                        {{ searchLoading ? 'Searching...' : 'Search by Tags' }}
                      </button>
                      <button
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        @click="loadAllImages"
                        :disabled="imagesLoading"
                      >
                        Show All
                      </button>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Image Display Area -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">
                <i class="bi bi-grid-3x3-gap-fill me-2"></i>
                {{ currentViewTitle }}
              </h5>
              <div class="d-flex align-items-center">
                <span class="text-muted me-3">Total {{ images.length }} images</span>
                <div class="btn-group" role="group">
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    :class="{ active: sortBy === 'date' }"
                    @click="sortBy = 'date'"
                  >
                    By Date
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    :class="{ active: sortBy === 'name' }"
                    @click="sortBy = 'name'"
                  >
                    By Name
                  </button>
                </div>
              </div>
            </div>
            <div class="card-body">
              <ImageGrid
                :images="sortedImages"
                :loading="imagesLoading"
                :empty-message="emptyMessage"
                :empty-sub-message="emptySubMessage"
                @update-tags="handleUpdateTags"
                @delete-image="handleDeleteImage"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import AppHeader from '../components/AppHeader.vue';
import ImageGrid from '../components/ImageGrid.vue';
import apiClient from '@/api/axios.js';

// Reactive data
const images = ref([]);
const imagesLoading = ref(false);
const searchLoading = ref(false);
const isSearchActive = ref(false);
const sortBy = ref('date');

const searchForm = reactive({
  tags: '',
  confidence: 50
});

// Computed properties
const totalImages = computed(() => images.value.length);

const identifiedImages = computed(() => 
  images.value.filter(img => img.predictions && img.predictions.length > 0).length
);

const totalTags = computed(() => {
  const allTags = images.value.flatMap(img => img.tags || []);
  return new Set(allTags).size;
});

const thisWeekUploads = computed(() => {
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  return images.value.filter(img => new Date(img.uploadedAt) > oneWeekAgo).length;
});

const currentViewTitle = computed(() => 
  isSearchActive.value ? 'Search Results' : 'All Images'
);

const emptyMessage = computed(() => 
  isSearchActive.value ? 'No matching images found' : 'No images yet'
);

const emptySubMessage = computed(() => 
  isSearchActive.value ? 'Try adjusting your search criteria' : 'Upload some images to start identifying birds!'
);

const sortedImages = computed(() => {
  const imagesCopy = [...images.value];
  if (sortBy.value === 'date') {
    return imagesCopy.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));
  } else {
    return imagesCopy.sort((a, b) => a.filename.localeCompare(b.filename));
  }
});

// Methods
const loadAllImages = async () => {
  imagesLoading.value = true;
  isSearchActive.value = false;
  
  try {
    console.log('Loading all images from API...');
    
    // Call the backend API to get all files
    const response = await apiClient.get('/files');
    
    console.log('✅ Loaded images from API:', response.data?.length || 0);
    
    // Handle different response formats
    let files = [];
    if (response.data && response.data.files && Array.isArray(response.data.files)) {
      files = response.data.files;
    } else if (Array.isArray(response.data)) {
      files = response.data;
    }
    

    
    // Transform the response to match our component structure
    if (files.length > 0) {
      images.value = files.map(file => {
        
        // Parse AI tags from backend
        let aiData = { species: [], confidence: 0, description: '' };
        if (file.ai_tags) {
          try {
            aiData = typeof file.ai_tags === 'string' ? JSON.parse(file.ai_tags) : file.ai_tags;
            console.log('Parsed AI tags:', aiData);
          } catch (e) {
            console.error('Error parsing ai_tags:', e, file.ai_tags);
          }
        }

        // Convert AI data to frontend format
        const predictions = aiData.species && aiData.species.length > 0 ? 
          aiData.species.map(species => ({
            label: species,
            confidence: aiData.confidence || 0
          })) : 
          (file.predictions || file.aiResults || file.analysis || []);

        const tags = aiData.species && aiData.species.length > 0 ? 
          [...aiData.species] : 
          (file.tags || []);

        const processedFile = {
          id: file.id || file.fileId || file.media_id || file.filename || Math.random().toString(36),
          filename: file.filename || file.name || file.originalName || 'unknown',
          url: file.original_url || file.url || file.s3_url || file.fileUrl || file.downloadUrl || '',
          thumbnailUrl: file.thumbnail_url || file.thumbnailUrl || file.thumbnail || file.original_url || '',
          uploadedAt: file.uploadedAt || file.createdAt || file.timestamp || new Date().toISOString(),
          predictions: predictions,
          tags: tags,
          description: aiData.description || '', // For Recognition Results
          // Add debugging info for image loading issues
          originalData: {
            media_id: file.media_id,
            original_url: file.original_url,
            thumbnail_url: file.thumbnail_url
          }
        };
        console.log('Processed file result:', processedFile);
        console.log('Image URL for display:', processedFile.url);
        console.log('Thumbnail URL for display:', processedFile.thumbnailUrl);
        
        // Test if image URLs are accessible
        if (processedFile.url) {
          fetch(processedFile.url, { method: 'HEAD' })
            .then(response => {
              console.log(`Image ${processedFile.filename} URL status:`, response.status, response.ok ? '✅' : '❌');
            })
            .catch(error => {
              console.log(`Image ${processedFile.filename} URL error:`, error.message, '❌');
            });
        }
        return processedFile;
      });
    } else {
      console.warn('No files found in response:', response.data);
      images.value = [];
    }
    
    ElMessage.success(`Loaded ${images.value.length} images`);
    
  } catch (error) {
    console.error('Error loading images:', error);
    ElMessage.error('Failed to load images. Please try again.');
    images.value = [];
  } finally {
    imagesLoading.value = false;
  }
};

const performSearch = async () => {
  if (!searchForm.tags.trim()) {
    ElMessage.warning('Please enter tags to search');
    return;
  }

  searchLoading.value = true;
  isSearchActive.value = true;

  try {
    console.log('Performing search with criteria:', {
      tags: searchForm.tags,
      confidence: searchForm.confidence / 100
    });

    // Call the backend API for tag-based search
    const response = await apiClient.post('/query/by-tags', {
      tags: searchForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
      minConfidence: searchForm.confidence / 100
    });
    
    console.log('Search response:', response.data);
    
    // Handle different response formats
    let searchResults = [];
    if (response.data && response.data.links) {
      // If response contains links array
      searchResults = response.data.links.map((url, index) => ({
        id: `search-${index}`,
        filename: url.split('/').pop() || `image-${index}`,
        url: url,
        thumbnailUrl: url,
        uploadedAt: new Date().toISOString(),
        predictions: [],
        tags: searchForm.tags.split(',').map(tag => tag.trim())
      }));
    } else if (response.data && response.data.files) {
      searchResults = response.data.files;
    } else if (Array.isArray(response.data)) {
      searchResults = response.data;
    }
    
    images.value = searchResults;
    ElMessage.success(`Found ${searchResults.length} matching images`);
    
  } catch (error) {
    console.error('Error performing search:', error);
    ElMessage.error('Search failed. Please try again.');
    images.value = [];
  } finally {
    searchLoading.value = false;
  }
};

const handleUpdateTags = async (imageId, tags) => {
  try {
    console.log('Updating tags for image:', imageId, tags);
    
    // Call backend API to update tags
    await apiClient.post('/tags/update', {
      fileId: imageId,
      tags: tags
    });
    
    // Update local data
    const imageIndex = images.value.findIndex(img => img.id === imageId);
    if (imageIndex !== -1) {
      images.value[imageIndex].tags = tags;
    }
    
    ElMessage.success('Tags updated successfully');
    console.log('Tags updated successfully');
    
  } catch (error) {
    console.error('Error updating tags:', error);
    ElMessage.error('Failed to update tags. Please try again.');
  }
};

const handleDeleteImage = async (imageId) => {
  try {
    // Find the image to get its URL
    const image = images.value.find(img => img.id === imageId);
    
    // Add detailed debugging to see what we have
    console.log('Object received by handleDeleteImage - imageId:', imageId);
    console.log('Object received by handleDeleteImage - full image object:', image);
    console.log('Available image properties:', image ? Object.keys(image) : 'No image found');
    
    // Show the actual values of each property to understand the data structure
    if (image) {
      console.log('Detailed image object contents:');
      Object.keys(image).forEach(key => {
        console.log(`  ${key}:`, image[key]);
      });
    }
    
    if (!image) {
      ElMessage.error('Image not found');
      return;
    }

    // Check for URL in different possible property names
    // Note: empty strings are falsy, so we need to check for actual content
    const imageUrl = (image.url && image.url.trim()) || 
                     (image.original_url && image.original_url.trim()) ||
                     (image.s3_url && image.s3_url.trim()) || 
                     (image.fileUrl && image.fileUrl.trim()) || 
                     (image.src && image.src.trim());
    console.log('Image URL candidates:', {
      'image.url': image.url,
      'image.original_url': image.original_url,
      'image.s3_url': image.s3_url,
      'image.fileUrl': image.fileUrl,
      'image.src': image.src,
      'selected': imageUrl
    });

    if (!imageUrl) {
      ElMessage.error('Cannot find image URL for deletion');
      console.error('No valid URL found in image object:', image);
      return;
    }

    // Confirm deletion
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${image.filename || image.name || 'this image'}"? This action cannot be undone.`,
      'Confirm Deletion',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    );

    console.log('Deleting image:', imageId, imageUrl);
    
    // Extract filename from URL for backend API
    // Backend expects just the filename, not the full URL
    const filename = imageUrl.split('/').pop();
    console.log('Extracted filename:', filename);
    
    // Call backend API to delete file
    console.log('Sending delete request with payload:', { urls: [filename] });
    const deleteResponse = await apiClient.post('/admin/files', {
      
      
      urls: [filename]
    });
    console.log('✅ Delete successful:', deleteResponse.status);
    
    ElMessage.success('Image deleted successfully');
    
    // Reload data from backend to get updated list
    console.log('Reloading images from backend after deletion...');
    console.log('Images count before reload:', images.value.length);
    await loadAllImages();
    console.log('Images count after reload:', images.value.length);
    console.log('Images reloaded successfully after deletion');
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Error deleting image:', error);
      ElMessage.error('Failed to delete image. Please try again.');
    }
  }
  };

// Lifecycle
onMounted(() => {
  loadAllImages();
});
</script>

<style scoped>
.dashboard {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-card {
  border: none;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.search-card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.form-control, .form-select {
  border-left: none;
}

.form-control:focus, .form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.btn-group .btn.active {
  background-color: #667eea;
  border-color: #667eea;
  color: white;
}

@media (max-width: 768px) {
  .welcome-section .col-md-4 {
    text-align: center !important;
    margin-top: 1rem;
  }
  
  .stats-card {
    margin-bottom: 1rem;
  }
}
</style>