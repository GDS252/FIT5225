# Bird Recognition System - Frontend Application

This is a Vue.js and Bootstrap-based frontend application for a bird recognition system, integrated with AWS Cognito user authentication and API Gateway backend services.

## Features

### 🔐 User Authentication
- User registration and email verification
- Secure login/logout
- AWS Cognito-based identity authentication

### 📸 Image Management
- Drag and drop upload for multiple images
- Real-time upload progress display
- Image preview and management
- Support for JPG, PNG, GIF formats

### 🤖 AI Recognition
- Automatic bird species recognition
- Confidence score display
- Recognition result visualization

### 🏷️ Tag System
- Custom image tagging
- Tag editing and management
- Tag-based search

### 🔍 Search Functionality
- Keyword search
- Tag filtering
- Time range filtering
- Multi-condition combined search

## Tech Stack

- **Frontend Framework**: Vue.js 3
- **UI Framework**: Bootstrap 5
- **Routing**: Vue Router 4
- **HTTP Client**: Axios
- **AWS Integration**: AWS Amplify
- **Build Tool**: Vite
- **Icons**: Bootstrap Icons

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── AppHeader.vue   # Application header navigation
│   └── ImageGrid.vue   # Image grid display
├── views/              # Page components
│   ├── LoginView.vue   # Login page
│   ├── RegisterView.vue # Registration page
│   ├── DashboardView.vue # Main dashboard
│   └── UploadView.vue  # File upload page
├── router/             # Routing configuration
│   └── index.js        # Route definitions and guards
├── aws-exports.js      # AWS configuration file
├── App.vue            # Root component
└── main.js            # Application entry point
```

## Installation and Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure AWS Services
Edit the `src/aws-exports.js` file and update the following configuration:

```javascript
const awsconfig = {
  Auth: {
    region: 'your-aws-region',                    // Your AWS region
    userPoolId: 'your-cognito-user-pool-id',     // Cognito User Pool ID
    userPoolWebClientId: 'your-app-client-id',   // App Client ID
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
      bucket: 'your-s3-bucket-name',             // S3 bucket name
      region: 'your-aws-region'
    }
  }
}
```

### 3. Start Development Server
```bash
npm run dev
```

The application will start at `http://localhost:5173`.

### 4. Build for Production
```bash
npm run build
```

## Page Descriptions

### Login Page (`/login`)
- User email and password login
- Responsive design with mobile support
- Error handling and user feedback

### Registration Page (`/register`)
- New user registration
- Email verification process
- Password strength validation

### Main Dashboard (`/`)
- Image statistics overview
- Search and filter functionality
- Image grid display
- Tag editing and deletion operations

### Upload Page (`/upload`)
- Drag and drop upload support
- Batch file processing
- Real-time upload progress
- File format validation

## API Integration

Application integration points with backend APIs:

- `POST /files` - Get upload presigned URL
- `GET /files` - Get user file list
- `POST /query/search` - Search files
- `POST /tags/update` - Update file tags
- `POST /admin/files/delete` - Delete files
- `POST /files/process` - Trigger file processing

## Route Guards

The application uses Vue Router guards to protect authenticated pages:
- Unauthenticated users accessing protected pages are redirected to login
- Authenticated users accessing login/register pages are redirected to home

## Responsive Design

The application fully supports responsive design:
- Mobile-optimized interface
- Touch-friendly interactions
- Adaptive layout

## Browser Support

- Chrome (Recommended)
- Firefox
- Safari
- Edge

## Development Notes

1. **AWS Configuration**: Ensure proper AWS service credentials configuration
2. **CORS Settings**: API Gateway needs proper CORS configuration
3. **File Size**: Default limit of 10MB per file
4. **Image Formats**: Supports common image formats (JPG, PNG, GIF)

## Troubleshooting

### Common Issues

1. **Login Failure**
   - Check AWS Cognito configuration
   - Verify User Pool and App Client settings

2. **Upload Failure**
   - Check S3 bucket permissions
   - Verify API Gateway configuration

3. **Images Not Displaying**
   - Check S3 bucket public access settings
   - Verify CloudFront configuration (if used)

## License

MIT License
