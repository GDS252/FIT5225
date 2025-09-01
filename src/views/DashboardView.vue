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
              
              <!-- Search Type Tabs -->
              <ul class="nav nav-tabs mb-3" id="searchTabs" role="tablist">
                <li class="nav-item" role="presentation">
                  <button 
                    class="nav-link"
                    :class="{ active: searchType === 'tags' }"
                    @click="searchType = 'tags'"
                    type="button"
                  >
                    <i class="bi bi-tags me-1"></i>
                    Search by Tags
                  </button>
                </li>
                <li class="nav-item" role="presentation">
                  <button 
                    class="nav-link"
                    :class="{ active: searchType === 'thumbnail' }"
                    @click="searchType = 'thumbnail'"
                    type="button"
                  >
                    <i class="bi bi-image me-1"></i>
                    Find by Thumbnail
                  </button>
                </li>
              </ul>
              
              <!-- Tag Search Form -->
              <form v-if="searchType === 'tags'" @submit.prevent="performTagSearch">
                <div class="row g-3">
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
                    </div>
                  </div>
                </div>
              </form>
              

              
              <!-- Thumbnail Search Form -->
              <form v-if="searchType === 'thumbnail'" @submit.prevent="performThumbnailSearch">
                <div class="row g-3">
                  <div class="col-md-9">
                    <label for="thumbnailUrl" class="form-label">Thumbnail URL</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-link"></i>
                      </span>
                      <input
                        type="url"
                        class="form-control"
                        id="thumbnailUrl"
                        v-model="searchForm.thumbnailUrl"
                        placeholder="https://bucket.s3.amazonaws.com/thumb_filename.jpg"
                      />
                    </div>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">&nbsp;</label>
                    <div class="d-grid gap-2">
                      <button
                        type="submit"
                        class="btn btn-info"
                        :disabled="searchLoading"
                      >
                        <span v-if="searchLoading" class="spinner-border spinner-border-sm me-2"></span>
                        {{ searchLoading ? 'Finding...' : 'Find Original' }}
                      </button>
                    </div>
                  </div>
                </div>
              </form>
              
              <!-- Common Controls -->
              <div class="row mt-3">
                <div class="col-12">
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm me-2"
                    @click="clearSearch"
                    :disabled="imagesLoading"
                  >
                    <i class="bi bi-x-circle me-1"></i>
                    Clear & Show All
                  </button>
                  <small class="text-muted">
                    Use different search types to find images by tags or locate originals from thumbnails.
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Image Display Area -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <div class="row align-items-center">
                <div class="col-md-4">
                  <h5 class="card-title mb-0">
                    <i class="bi bi-grid-3x3-gap-fill me-2"></i>
                    {{ currentViewTitle }}
                  </h5>
                </div>
                <div class="col-md-4 text-center">
                  <!-- Bulk Selection Controls -->
                  <div v-if="images.length > 0" class="btn-group" role="group">
                    <button
                      type="button"
                      class="btn btn-sm"
                      :class="bulkSelectMode ? 'btn-primary' : 'btn-outline-primary'"
                      @click="toggleBulkSelectMode"
                    >
                      <i class="bi bi-check-square me-1"></i>
                      {{ bulkSelectMode ? 'Exit Select' : 'Bulk Select' }}
                    </button>
                    <button
                      v-if="bulkSelectMode"
                      type="button"
                      class="btn btn-outline-secondary btn-sm"
                      @click="selectAllImages"
                    >
                      <i class="bi bi-check-all me-1"></i>
                      {{ selectedImages.length === images.length ? 'Deselect All' : 'Select All' }}
                    </button>
                    <button
                      v-if="bulkSelectMode && selectedImages.length > 0"
                      type="button"
                      class="btn btn-outline-success btn-sm"
                      data-bs-toggle="modal"
                      data-bs-target="#bulkTagModal"
                    >
                      <i class="bi bi-tags me-1"></i>
                      Manage Tags ({{ selectedImages.length }})
                    </button>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="d-flex align-items-center justify-content-end">
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
              </div>
            </div>
            <div class="card-body">
              <ImageGrid
                :images="sortedImages"
                :loading="imagesLoading"
                :empty-message="emptyMessage"
                :empty-sub-message="emptySubMessage"
                :bulk-select-mode="bulkSelectMode"
                :selected-images="selectedImages"
                @update-tags="handleUpdateTags"
                @delete-image="handleDeleteImage"
                @toggle-selection="toggleImageSelection"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Tag Manager Modal -->
    <BulkTagManager 
      :selected-images="selectedImages"
      @tags-updated="handleTagsUpdated"
    />

    <!-- Email Subscription Footer -->
    <EmailSubscription />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import AppHeader from '../components/AppHeader.vue';
import ImageGrid from '../components/ImageGrid.vue';
import BulkTagManager from '../components/BulkTagManager.vue';
import EmailSubscription from '../components/EmailSubscription.vue';
import apiClient from '@/api/axios.js';

// Reactive data
const images = ref([]);
const imagesLoading = ref(false);
const searchLoading = ref(false);
const isSearchActive = ref(false);
const sortBy = ref('date');
const searchType = ref('tags'); // 'tags', 'thumbnail'

// Bulk selection state
const selectedImages = ref([]);
const bulkSelectMode = ref(false);

const searchForm = reactive({
  tags: '',
  thumbnailUrl: '',
  confidence: 50
});

// Computed properties
const totalImages = computed(() => images.value.length);

const identifiedImages = computed(() => {
  const identified = images.value.filter(img => img.predictions && img.predictions.length > 0);
  console.log('🔍 Computing identifiedImages:');
  console.log('Total images:', images.value.length);
  console.log('Images with predictions:', identified.length);
  console.log('Sample predictions:', identified.slice(0, 2).map(img => ({
    filename: img.filename,
    predictions: img.predictions
  })));
  return identified.length;
});

const totalTags = computed(() => {
  const allTags = images.value.flatMap(img => img.tags || []);
  const uniqueTags = new Set(allTags);
  console.log('🏷️ Computing totalTags:');
  console.log('All tags array:', allTags);
  console.log('Unique tags:', Array.from(uniqueTags));
  console.log('Total unique tags count:', uniqueTags.size);
  return uniqueTags.size;
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

        console.log('📊 Processing file for statistics:', {
          filename: file.filename,
          aiData: aiData,
          predictions: predictions,
          tags: tags,
          hasAiTags: !!file.ai_tags
        });

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
        
        // URL accessibility testing removed to avoid CORS issues
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

// Clear search and show all images
const clearSearch = () => {
  searchForm.tags = '';
  searchForm.thumbnailUrl = '';
  searchType.value = 'tags';
  loadAllImages();
};

// Bulk selection methods
const toggleBulkSelectMode = () => {
  console.log('🔄 [DashboardView] Toggling bulk select mode');
  console.log('📊 [DashboardView] Current bulk select mode:', bulkSelectMode.value);
  
  bulkSelectMode.value = !bulkSelectMode.value;
  
  console.log('📊 [DashboardView] New bulk select mode:', bulkSelectMode.value);
  
  if (!bulkSelectMode.value) {
    console.log('🧹 [DashboardView] Clearing selected images');
    selectedImages.value = [];
  }
  
  console.log('✅ [DashboardView] Bulk select mode toggled successfully');
};

const toggleImageSelection = (image) => {
  console.log('🖱️ [DashboardView] Toggling image selection');
  console.log('🖼️ [DashboardView] Image to toggle:', { id: image.id, filename: image.filename });
  
  const index = selectedImages.value.findIndex(img => img.id === image.id);
  console.log('📍 [DashboardView] Current selection index:', index);
  
  if (index > -1) {
    selectedImages.value.splice(index, 1);
    console.log('➖ [DashboardView] Image removed from selection');
  } else {
    selectedImages.value.push(image);
    console.log('➕ [DashboardView] Image added to selection');
  }
  
  console.log('📊 [DashboardView] Total selected images:', selectedImages.value.length);
  console.log('🏷️ [DashboardView] Selected image IDs:', selectedImages.value.map(img => img.id));
};

const selectAllImages = () => {
  console.log('🔲 [DashboardView] Select all images triggered');
  console.log('📊 [DashboardView] Current selection count:', selectedImages.value.length);
  console.log('📊 [DashboardView] Total available images:', images.value.length);
  
  if (selectedImages.value.length === images.value.length) {
    selectedImages.value = [];
    console.log('🧹 [DashboardView] All images deselected');
  } else {
    selectedImages.value = [...images.value];
    console.log('✅ [DashboardView] All images selected');
  }
  
  console.log('📊 [DashboardView] Final selection count:', selectedImages.value.length);
};

const isImageSelected = (image) => {
  const selected = selectedImages.value.some(img => img.id === image.id);
  // Only log occasionally to avoid spam
  if (Math.random() < 0.01) { // 1% chance to log
    console.log('🔍 [DashboardView] Checking image selection:', { id: image.id, selected });
  }
  return selected;
};

// Handle tags updated event from BulkTagManager
const handleTagsUpdated = () => {
  console.log('🔄 [DashboardView] Handling tags updated event');
  console.log('📊 [DashboardView] Previously selected images count:', selectedImages.value.length);
  
  // Refresh the images after bulk tag update
  console.log('🔄 [DashboardView] Refreshing images after bulk tag update');
  loadAllImages();
  
  // Clear selection
  console.log('🧹 [DashboardView] Clearing selection after tag update');
  selectedImages.value = [];
  bulkSelectMode.value = false;
  
  console.log('✅ [DashboardView] Tags updated handling completed');
};

// Tag search (existing functionality)
const performTagSearch = async () => {
  if (!searchForm.tags.trim()) {
    ElMessage.warning('Please enter tags to search');
    return;
  }
  await performSearch('tags');
};



// Thumbnail to original search
const performThumbnailSearch = async () => {
  if (!searchForm.thumbnailUrl.trim()) {
    ElMessage.warning('Please enter a thumbnail URL');
    return;
  }
  await performSearch('thumbnail');
};

// Unified search function
const performSearch = async (type = 'tags') => {
  console.log('🔍 [DashboardView] Starting search process');
  console.log('🎯 [DashboardView] Search type:', type);
  
  searchLoading.value = true;
  isSearchActive.value = true;

  try {
    let response;
    let searchCriteria = {};

    if (type === 'tags') {
      // Tag-based search
      const tagArray = searchForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag);
      searchCriteria = {
        tags: searchForm.tags,
        confidence: searchForm.confidence / 100
      };
      console.log('🏷️ [DashboardView] Tag search criteria:', searchCriteria);
      console.log('📝 [DashboardView] Parsed tags array:', tagArray);
      
      const requestPayload = {
        tags: tagArray,
        minConfidence: searchForm.confidence / 100
      };
      console.log('📤 [DashboardView] Tag search request payload:', requestPayload);
      console.log('🎯 [DashboardView] Sending request to /query/by-tags');
      
      response = await apiClient.post('/query/by-tags', requestPayload);
      
    } else if (type === 'thumbnail') {
      // Thumbnail to original search
      searchCriteria = { thumbnailUrl: searchForm.thumbnailUrl };
      console.log('🖼️ [DashboardView] Thumbnail search criteria:', searchCriteria);
      console.log('🔗 [DashboardView] Thumbnail URL to search:', searchForm.thumbnailUrl.trim());
      console.log('🎯 [DashboardView] Sending request to /query/by-thumbnail');
      
      try {
        const requestParams = {
          url: searchForm.thumbnailUrl.trim()
        };
        console.log('📤 [DashboardView] Thumbnail search params:', requestParams);
        
        response = await apiClient.get('/query/by-thumbnail', {
          params: requestParams
        });
        
        console.log('✅ [DashboardView] Thumbnail search response received:', response);
      } catch (apiError) {
        console.warn('⚠️ [DashboardView] Thumbnail API error, attempting local fallback:', apiError);
        console.log('🔄 [DashboardView] Loading all images for local search...');
        
        // Fallback to local search
        await loadAllImages();
        const foundImage = images.value.find(image => 
          image.thumbnailUrl === searchForm.thumbnailUrl.trim() ||
          image.thumbnail_url === searchForm.thumbnailUrl.trim()
        );
        
        console.log('🔍 [DashboardView] Local search result:', foundImage);
        
        if (foundImage) {
          images.value = [foundImage];
          console.log('🎉 [DashboardView] Found image locally');
          ElMessage.success('Found the original image!');
        } else {
          images.value = [];
          console.log('❌ [DashboardView] No matching image found locally');
          ElMessage.warning('No matching image found for this thumbnail URL');
        }
        return;
      }
    }
    
    console.log('📊 [DashboardView] Search response status:', response.status);
    console.log('📄 [DashboardView] Search response data:', response.data);
    
    // Handle different response formats
    let searchResults = [];
    
    if (type === 'thumbnail' && response.data && response.data.original_url) {
      // Handle thumbnail search response - single image result
      console.log('🖼️ [DashboardView] Processing thumbnail search response');
      console.log('🔗 [DashboardView] Original URL found:', response.data.original_url);
      
      searchResults = [{
        id: `thumbnail-search-${Date.now()}`,
        filename: response.data.original_url.split('/').pop() || 'found-image',
        url: response.data.original_url,
        thumbnailUrl: searchForm.thumbnailUrl,
        uploadedAt: new Date().toISOString(),
        predictions: [],
        tags: []
      }];
      console.log('✅ [DashboardView] Thumbnail search result created:', searchResults[0]);
      
    } else if (type === 'thumbnail' && response.data && response.data.message) {
      // Handle no matching image found
      console.log('❌ [DashboardView] No matching image found:', response.data.message);
      searchResults = [];
      
    } else if (response.data && response.data.links) {
      // If response contains links array
      console.log('🔗 [DashboardView] Processing links array response');
      console.log('📊 [DashboardView] Links count:', response.data.links.length);
      
      searchResults = response.data.links.map((url, index) => ({
        id: `search-${index}`,
        filename: url.split('/').pop() || `image-${index}`,
        url: url,
        thumbnailUrl: url,
        uploadedAt: new Date().toISOString(),
        predictions: [],
        tags: searchForm.tags.split(',').map(tag => tag.trim())
      }));
      console.log('✅ [DashboardView] Links processed into search results:', searchResults.length);
      
    } else if (response.data && response.data.files) {
      // Process search results same as regular files
      searchResults = response.data.files.map(file => {
        // Parse AI tags from backend
        let aiData = { species: [], confidence: 0, description: '' };
        if (file.ai_tags) {
          try {
            aiData = typeof file.ai_tags === 'string' ? JSON.parse(file.ai_tags) : file.ai_tags;
          } catch (e) {
            console.error('Error parsing ai_tags in search:', e, file.ai_tags);
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

        return {
          id: file.id || file.fileId || file.media_id || file.filename || Math.random().toString(36),
          filename: file.filename || file.name || file.originalName || 'unknown',
          url: file.original_url || file.url || file.s3_url || file.fileUrl || file.downloadUrl || '',
          thumbnailUrl: file.thumbnail_url || file.thumbnailUrl || file.thumbnail || file.original_url || '',
          uploadedAt: file.uploadedAt || file.createdAt || file.timestamp || new Date().toISOString(),
          predictions: predictions,
          tags: tags,
          description: aiData.description || ''
        };
      });
    } else if (Array.isArray(response.data)) {
      searchResults = response.data;
    }
    
    images.value = searchResults;
    
    // Show appropriate success message
    if (type === 'tags') {
      ElMessage.success(`Found ${searchResults.length} images matching tags: ${searchForm.tags}`);
    } else if (type === 'thumbnail') {
      ElMessage.success(`Found original image for thumbnail`);
    }
    
  } catch (error) {
    console.error('❌ [DashboardView] Error performing search:', error);
    console.error('🔍 [DashboardView] Search error details:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      searchType: type,
      searchCriteria: searchCriteria,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers
      }
    });
    
    if (error.response?.status === 500) {
      console.error('💥 [DashboardView] Server error during search');
      ElMessage.error('Search service error. The backend search functionality may need to be implemented or fixed.');
    } else if (error.response?.status === 404) {
      console.error('🔍 [DashboardView] Search endpoint not found');
      ElMessage.error('Search endpoint not found. Please check the API configuration.');
    } else if (error.response?.status === 400) {
      console.warn('⚠️ [DashboardView] Bad request - invalid search parameters');
      ElMessage.error('Invalid search parameters. Please check your input.');
    } else if (!error.response) {
      console.error('🌐 [DashboardView] Network error - no response received');
      ElMessage.error('Network error. Please check your connection and try again.');
    } else {
      console.error('🚫 [DashboardView] Unknown search error occurred');
      ElMessage.error('Search failed. Please try again.');
    }
    
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