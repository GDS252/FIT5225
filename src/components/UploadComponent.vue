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
  
  if (!fileItem) {
    ElMessage.error('File not found in upload list')
    return
  }

  try {
    fileItem.status = 'uploading'
    fileItem.progress = 10

    console.log('Starting upload for file:', file.name)

    // Step 1: Get presigned URL from backend
    const presignResponse = await apiClient.post('/files', {
      fileName: file.name,
      fileType: file.type,
      fileSize: file.size
    })

    console.log('Presigned URL response:', presignResponse.data)
    fileItem.progress = 20

    const { url, fields, fileId } = presignResponse.data

    // Step 2: Upload file to S3 using presigned URL
    const formData = new FormData()
    
    // Add all fields from presigned URL
    if (fields) {
      Object.entries(fields).forEach(([key, value]) => {
        formData.append(key, value)
      })
    }
    
    // Add the file (must be last)
    formData.append('file', file)

    // Upload to S3 with progress tracking
    await axios.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 80) / progressEvent.total) + 20
        fileItem.progress = Math.min(progress, 95)
      }
    })

    console.log('File uploaded to S3 successfully:', file.name)
    fileItem.progress = 95

    // Step 3: Notify backend that upload is complete (optional)
    try {
      await apiClient.post('/files/process', {
        fileId: fileId,
        fileName: file.name
      })
      console.log('Backend notified of successful upload')
    } catch (processError) {
      console.warn('Failed to notify backend, but upload was successful:', processError)
    }

    // Mark as complete
    fileItem.progress = 100
    fileItem.status = 'success'
    
    ElMessage.success(`${file.name} uploaded successfully!`)
    emit('upload-success', { file, fileId })

    // Remove from list after successful upload
    setTimeout(() => {
      removeFile(fileItem)
    }, 2000)

  } catch (error) {
    console.error('Upload failed:', error)
    fileItem.status = 'exception'
    fileItem.progress = 0
    
    let errorMessage = 'Upload failed'
    if (error.response) {
      errorMessage = `Upload failed: ${error.response.status} ${error.response.statusText}`
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
