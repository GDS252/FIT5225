# 鸟类识别系统 - 前端应用

这是一个基于Vue.js和Bootstrap构建的鸟类识别系统前端应用，集成了AWS Cognito用户认证和API Gateway后端服务。

## 功能特性

### 🔐 用户认证
- 用户注册和邮箱验证
- 安全登录/登出
- 基于AWS Cognito的身份验证

### 📸 图片管理
- 支持拖拽上传多张图片
- 实时上传进度显示
- 图片预览和管理
- 支持JPG、PNG、GIF格式

### 🤖 AI识别
- 自动鸟类品种识别
- 置信度评分显示
- 识别结果可视化

### 🏷️ 标签系统
- 自定义图片标签
- 标签编辑和管理
- 基于标签的搜索

### 🔍 搜索功能
- 关键词搜索
- 标签过滤
- 时间范围筛选
- 多条件组合搜索

## 技术栈

- **前端框架**: Vue.js 3
- **UI框架**: Bootstrap 5
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **AWS集成**: AWS Amplify
- **构建工具**: Vite
- **图标**: Bootstrap Icons

## 项目结构

```
src/
├── components/          # 可复用组件
│   ├── AppHeader.vue   # 应用头部导航
│   └── ImageGrid.vue   # 图片网格展示
├── views/              # 页面组件
│   ├── LoginView.vue   # 登录页面
│   ├── RegisterView.vue # 注册页面
│   ├── DashboardView.vue # 主仪表板
│   └── UploadView.vue  # 文件上传页面
├── router/             # 路由配置
│   └── index.js        # 路由定义和守卫
├── aws-exports.js      # AWS配置文件
├── App.vue            # 根组件
└── main.js            # 应用入口
```

## 安装和运行

### 1. 安装依赖
```bash
npm install
```

### 2. 配置AWS服务
编辑 `src/aws-exports.js` 文件，更新以下配置：

```javascript
const awsconfig = {
  Auth: {
    region: 'your-aws-region',                    // 您的AWS区域
    userPoolId: 'your-cognito-user-pool-id',     // Cognito用户池ID
    userPoolWebClientId: 'your-app-client-id',   // 应用客户端ID
    // ...
  },
  API: {
    endpoints: [
      {
        name: 'birdRecognitionAPI',
        endpoint: 'your-api-gateway-url',         // API Gateway URL
        region: 'your-aws-region'
      }
    ]
  },
  Storage: {
    AWSS3: {
      bucket: 'your-s3-bucket-name',             // S3存储桶名称
      region: 'your-aws-region'
    }
  }
}
```

### 3. 启动开发服务器
```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 4. 构建生产版本
```bash
npm run build
```

## 页面说明

### 登录页面 (`/login`)
- 用户邮箱和密码登录
- 响应式设计，支持移动端
- 错误处理和用户反馈

### 注册页面 (`/register`)
- 新用户注册
- 邮箱验证流程
- 密码强度验证

### 主仪表板 (`/`)
- 图片统计概览
- 搜索和过滤功能
- 图片网格展示
- 标签编辑和删除操作

### 上传页面 (`/upload`)
- 拖拽上传支持
- 批量文件处理
- 实时上传进度
- 文件格式验证

## API集成

应用与后端API的集成点：

- `POST /files` - 获取上传预签名URL
- `GET /files` - 获取用户文件列表
- `POST /query/search` - 搜索文件
- `POST /tags/update` - 更新文件标签
- `POST /admin/files/delete` - 删除文件
- `POST /files/process` - 触发文件处理

## 路由守卫

应用使用Vue Router守卫来保护需要认证的页面：
- 未登录用户访问受保护页面会重定向到登录页
- 已登录用户访问登录/注册页会重定向到主页

## 响应式设计

应用完全支持响应式设计：
- 移动端优化的界面
- 触摸友好的交互
- 自适应布局

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 开发注意事项

1. **AWS配置**: 确保正确配置AWS服务凭证
2. **CORS设置**: API Gateway需要正确配置CORS
3. **文件大小**: 默认限制单文件10MB
4. **图片格式**: 支持常见图片格式 (JPG, PNG, GIF)

## 故障排除

### 常见问题

1. **登录失败**
   - 检查AWS Cognito配置
   - 确认用户池和应用客户端设置

2. **上传失败**
   - 检查S3存储桶权限
   - 确认API Gateway配置

3. **图片不显示**
   - 检查S3存储桶的公共访问设置
   - 确认CloudFront配置（如果使用）

## 许可证

MIT License
