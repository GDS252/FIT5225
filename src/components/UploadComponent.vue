<template>
  <div class="upload-component">
    <el-upload
      ref="uploadRef"
      action="#"
      :http-request="handleUpload"
      :show-file-list="false"
      :before-upload="beforeUpload"
      multiple
      accept="image/*"
      drag
    >
      <div class="upload-dragger">
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          Drop files here or <em>click to upload</em>
        </div>
        <div class="el-upload__tip">
          Supports JPG, PNG, GIF formats, max 10MB per file
        </div>
      </div>
    </el-upload>

    <!-- File List -->
    <div v-if="fileList.length > 0" class="file-list mt-4">
      <h6>Uploading Files:</h6>
      <div class="file-item" v-for="file in fileList" :key="file.uid">
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>
        <div class="file-progress">
          <el-progress 
            :percentage="file.progress" 
            :status="file.status"
            :stroke-width="6"
          />
        </div>
        <div class="file-actions">
          <el-button 
            v-if="file.status === 'exception'"
            size="small" 
            type="primary" 
            @click="retryUpload(file)"
          >
            Retry
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="removeFile(file)"
          >
            Remove
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import apiClient from '@/api/axios.js'
import axios from 'axios'

const emit = defineEmits(['upload-success', 'upload-error'])

const uploadRef = ref(null)
const fileList = ref([])

const beforeUpload = (file) => {
  // Check file type
  const isValidType = file.type.startsWith('image/')
  if (!isValidType) {
    ElMessage.error(`${file.name} is not a valid image file`)
    return false
  }

  // Check file size (10MB)
  const isValidSize = file.size / 1024 / 1024 < 10
  if (!isValidSize) {
    ElMessage.error(`${file.name} file size exceeds 10MB`)
    return false
  }

  // Add file to list with initial status
  const fileItem = {
    uid: file.uid,
    name: file.name,
    size: file.size,
    progress: 0,
    status: 'ready',
    file: file
  }
  fileList.value.push(fileItem)

  return true
}

const handleUpload = async (options) => {
  const file = options.file
  const fileItem = fileList.value.find(item => item.uid === file.uid)
  
  console.log('🚀 === UPLOAD DEBUGGING START ===')
  console.log('📁 File details:', {
    name: file.name,
    type: file.type,
    size: file.size,
    uid: file.uid,
    lastModified: file.lastModified
  })
  
  if (!fileItem) {
    console.error('❌ File not found in upload list')
    ElMessage.error('File not found in upload list')
    return
  }

  try {
    fileItem.status = 'uploading'
    fileItem.progress = 10

    console.log('🎯 Starting upload process for file:', file.name)
    console.log('📤 Step 1: Requesting presigned URL from backend...')

    // Step 1: Get presigned URL from backend
    // Backend will prepare S3 upload URL and register file metadata
    const requestPayload = {
      fileName: file.name,
      fileType: file.type,
      fileSize: file.size
    }
    
    console.log('📋 Request payload:', requestPayload)
    console.log('🌐 Making request to /files endpoint...')
    
    const presignResponse = await apiClient.post('/files', requestPayload)

    console.log('✅ Presigned URL response received!')
    console.log('📄 Full response data:', presignResponse.data)
    console.log('🔗 URL:', presignResponse.data.url)
    console.log('📝 Fields:', presignResponse.data.fields)
    console.log('🆔 File ID:', presignResponse.data.fileId)
    console.log('📊 Response status:', presignResponse.status)
    console.log('📊 Response headers:', presignResponse.headers)
    
    fileItem.progress = 20

    // Extract data with fallback property names
    const url = presignResponse.data.url || presignResponse.data.uploadUrl || presignResponse.data.presignedUrl
    const fields = presignResponse.data.fields || presignResponse.data.formData || {}
    const fileId = presignResponse.data.fileId || presignResponse.data.media_id || presignResponse.data.id || presignResponse.data.file_id
    
    console.log('📝 Extracted values:', { url, fields, fileId })
    
    // Validate critical response data
    if (!url) {
      console.error('❌ No upload URL found in response data:', presignResponse.data)
      throw new Error('❌ No upload URL received from backend')
    }
    
    console.log('🔍 Validating presigned URL response...')
    console.log('✓ URL exists:', !!url)
    console.log('✓ Fields exists:', !!fields)
    console.log('✓ FileID exists:', !!fileId)

    console.log('📤 Step 2: Preparing S3 upload...')
    
    // CRITICAL ANALYSIS: Check URL and fields structure
    console.log('🔍 ANALYZING PRESIGNED URL STRUCTURE...')
    console.log('🔗 Base URL:', url)
    console.log('🔗 URL ends with /:', url.endsWith('/'))
    console.log('📝 Fields structure:', fields)
    console.log('🗝️ S3 Key from fields:', fields?.key)
    
    // The backend is using presigned POST with fields.key pattern
    // This is actually CORRECT for S3 presigned POST uploads!
    if (url.endsWith('/') && fields?.key) {
      console.log('✅ DETECTED: Presigned POST pattern with fields.key')
      console.log('✅ This is the CORRECT S3 upload pattern!')
      console.log('✅ File will be uploaded to:', `${url}`)
      console.log('✅ S3 key will be:', fields.key)
    } else if (url.endsWith('/') && !fields?.key) {
      console.error('❌ INVALID: URL ends with / but no key in fields!')
      throw new Error('❌ Invalid presigned URL: missing both filename in URL and key in fields')
    } else {
      console.log('✅ DETECTED: Direct presigned URL (PUT pattern)')
    }
    
    // Step 2: Upload file directly to S3 using presigned URL
    // Once uploaded, S3 will automatically trigger backend processing (SNS -> Lambda)
    // No manual notification needed - the system is fully automated
    const formData = new FormData()
    
    // Add all fields from presigned URL
    if (fields) {
      console.log('📝 Adding presigned URL fields to FormData...')
      console.log('📝 Fields object:', fields)
      console.log('📝 Fields type:', typeof fields)
      console.log('📝 Fields keys:', Object.keys(fields))
      
      Object.entries(fields).forEach(([key, value]) => {
        formData.append(key, value)
        console.log(`✓ Added field: ${key} = ${value}`)
      })
    } else {
      console.warn('⚠️  No fields received from presigned URL response - this might be a PUT URL')
    }
    
    // Add the file (must be last)
    formData.append('file', file)
    console.log('✓ Added file to FormData:', {
      name: file.name, 
      type: file.type, 
      size: file.size,
      lastModified: new Date(file.lastModified).toISOString()
    })
    
    // Debug: Log all FormData entries
    console.log('📋 Complete FormData contents:')
    let formDataEntries = []
    for (let [key, value] of formData.entries()) {
      const logValue = key === 'file' ? `[File: ${value.name}, ${value.size} bytes]` : value
      console.log(`  ${key}: ${logValue}`)
      formDataEntries.push({ key, value: logValue })
    }
    console.log('📋 FormData summary:', formDataEntries)
    
    console.log('🌐 Uploading to S3 URL:', url)
    console.log('🌐 URL domain:', new URL(url).hostname)
    console.log('🌐 URL path:', new URL(url).pathname)

    // Upload to S3 with progress tracking
    // Check if this is a presigned POST URL (with fields) or presigned PUT URL (direct upload)
    let uploadResponse
    
    console.log('🚀 Starting S3 upload...')
    
    if (fields && Object.keys(fields).length > 0) {
      // Presigned POST URL - use FormData with fields
      console.log('📮 Using presigned POST upload with FormData and fields')
      console.log('📮 POST request details:', {
        url: url,
        method: 'POST',
        contentType: 'multipart/form-data',
        formDataFields: Object.keys(fields).length
      })
      
      uploadResponse = await axios.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 80) / progressEvent.total) + 20
          fileItem.progress = Math.min(progress, 95)
          console.log(`📊 Upload progress: ${progressEvent.loaded}/${progressEvent.total} bytes (${Math.round(progressEvent.loaded/progressEvent.total*100)}%)`)
        },
        timeout: 60000, // 60 second timeout
        validateStatus: (status) => {
          console.log(`📊 S3 response status: ${status}`)
          return status >= 200 && status < 400; // Accept 2xx and 3xx responses
        }
      })
    } else {
      // Presigned PUT URL - upload file directly
      console.log('📤 Using presigned PUT upload (direct file)')
      console.log('📤 PUT request details:', {
        url: url,
        method: 'PUT',
        contentType: file.type,
        fileSize: file.size
      })
      
      uploadResponse = await axios.put(url, file, {
        headers: {
          'Content-Type': file.type
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 80) / progressEvent.total) + 20
          fileItem.progress = Math.min(progress, 95)
          console.log(`📊 Upload progress: ${progressEvent.loaded}/${progressEvent.total} bytes (${Math.round(progressEvent.loaded/progressEvent.total*100)}%)`)
        },
        timeout: 60000, // 60 second timeout
        validateStatus: (status) => {
          console.log(`📊 S3 response status: ${status}`)
          return status >= 200 && status < 400; // Accept 2xx and 3xx responses
        }
      })
    }
    
    console.log('✅ S3 upload response received!')
    console.log('📄 Full upload response:', uploadResponse)
    console.log('📊 Response status:', uploadResponse.status)
    console.log('📊 Response statusText:', uploadResponse.statusText)
    console.log('📋 Response headers:', uploadResponse.headers)
    console.log('📄 Response data:', uploadResponse.data)
    console.log('📄 Response config URL:', uploadResponse.config?.url)

    // Check if upload was actually successful
    console.log('🔍 Validating S3 upload success...')
    console.log('🔍 Checking status codes: 200, 201, 204 are considered successful')
    
    // CRITICAL: Validate that the URL actually contains a file path
    const uploadUrl = uploadResponse.config?.url || url
    console.log('🔍 Upload URL analysis:', uploadUrl)
    
    // Check if URL contains the filename or a proper S3 key
    const urlPath = new URL(uploadUrl).pathname
    console.log('🔍 URL path:', urlPath)
    
    // If URL path is just "/" or empty, this indicates a problem with the presigned URL
    if (urlPath === '/' || urlPath === '') {
      console.error('❌ CRITICAL ERROR: Presigned URL has no file path!')
      console.error('❌ URL path is empty or just "/" - this means the file was not actually uploaded to S3')
      console.error('❌ Backend presigned URL generation is likely broken')
      throw new Error('❌ Presigned URL is invalid - missing file path. Backend needs to fix presigned URL generation.')
    }
    
    if (uploadResponse.status === 200 || uploadResponse.status === 201 || uploadResponse.status === 204) {
      console.log('🎉 SUCCESS: File uploaded to S3 successfully!')
      console.log('🎉 Final status:', uploadResponse.status)
      console.log('🎉 File details:', {
        name: file.name,
        size: file.size,
        type: file.type,
        fileId: fileId
      })
      
      // Construct the final S3 URL properly based on upload pattern
      let s3Url
      
      if (fields?.key) {
        // Presigned POST pattern: construct URL from base + key
        const baseUrl = url.split('?')[0].replace(/\/$/, '') // Remove trailing slash and query params
        s3Url = `${baseUrl}/${fields.key}`
        console.log('🔗 Constructed S3 URL from base + key:', s3Url)
      } else {
        // Direct presigned URL pattern
        s3Url = url.split('?')[0] // Remove query parameters
        console.log('🔗 Using direct presigned URL:', s3Url)
      }
      
      console.log('🔗 Constructed S3 file URL:', s3Url)
      console.log('🔗 S3 bucket from URL:', new URL(s3Url).hostname)
      console.log('🔗 S3 key from URL:', new URL(s3Url).pathname)
      
      // Mark as complete - backend will automatically process via S3 trigger
      fileItem.progress = 100
      fileItem.status = 'success'
      
      console.log('📡 File should now be available in S3 at:', s3Url)
      console.log('📡 Backend should automatically process this file via S3 event triggers')
      
      ElMessage.success(`${file.name} uploaded successfully!`)
      emit('upload-success', { file, fileId, s3Url })
    } else {
      console.error('❌ UPLOAD FAILED: Unexpected status code')
      throw new Error(`S3 upload failed with status: ${uploadResponse.status} ${uploadResponse.statusText}`)
    }

    // Remove from list after successful upload
    setTimeout(() => {
      removeFile(fileItem)
    }, 2000)
    
    console.log('🏁 === UPLOAD DEBUGGING END (SUCCESS) ===')

  } catch (error) {
    console.error('💥 === UPLOAD DEBUGGING END (ERROR) ===')
    console.error('❌ Upload failed with error:', error)
    console.error('❌ Error type:', error.constructor.name)
    console.error('❌ Error message:', error.message)
    
    if (error.response) {
      console.error('❌ Error response status:', error.response.status)
      console.error('❌ Error response statusText:', error.response.statusText)
      console.error('❌ Error response headers:', error.response.headers)
      console.error('❌ Error response data:', error.response.data)
      console.error('❌ Error response config:', error.response.config)
    }
    
    if (error.request) {
      console.error('❌ Error request:', error.request)
    }
    
    fileItem.status = 'exception'
    fileItem.progress = 0
    
    let errorMessage = 'Upload failed'
    if (error.response) {
      errorMessage = `Upload failed: ${error.response.status} ${error.response.statusText}`
      console.error('❌ Detailed error response:', error.response.data)
    } else if (error.message) {
      errorMessage = `Upload failed: ${error.message}`
    }
    
    ElMessage.error(errorMessage)
    emit('upload-error', { file, error })
  }
}

const retryUpload = (fileItem) => {
  fileItem.status = 'ready'
  fileItem.progress = 0
  handleUpload({ file: fileItem.file })
}

const removeFile = (fileItem) => {
  const index = fileList.value.findIndex(item => item.uid === fileItem.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Expose methods for parent component
defineExpose({
  clearFiles: () => {
    fileList.value = []
  },
  getFileList: () => fileList.value
})
</script>

<style scoped>
.upload-component {
  width: 100%;
}

.upload-dragger {
  padding: 40px;
  text-align: center;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.upload-dragger:hover {
  border-color: #409eff;
}

.el-icon--upload {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.el-upload__text {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 8px;
  background: #fafafa;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-right: 16px;
}

.file-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.file-size {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.file-progress {
  flex: 2;
  margin-right: 16px;
}

.file-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .file-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .file-info, .file-progress {
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .file-actions {
    justify-content: center;
  }
}
</style>
