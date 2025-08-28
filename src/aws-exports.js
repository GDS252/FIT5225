// AWS Amplify configuration
// Please update these values according to your AWS Cognito configuration
const awsconfig = {
  Auth: {
    region: 'us-east-1', // Please replace with your AWS region
    userPoolId: 'us-east-1_XXXXXXXXX', // Please replace with your Cognito User Pool ID
    userPoolWebClientId: 'xxxxxxxxxxxxxxxxxxxxxxxxxx', // Please replace with your Cognito App Client ID
    mandatorySignIn: true,
    authenticationFlowType: 'USER_SRP_AUTH'
  },
  API: {
    endpoints: [
      {
        name: 'birdRecognitionAPI',
        endpoint: 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/dev', // Please replace with your API Gateway URL
        region: 'us-east-1'
      }
    ]
  },
  Storage: {
    AWSS3: {
      bucket: 'your-s3-bucket-name', // Please replace with your S3 bucket name
      region: 'us-east-1'
    }
  }
}

export default awsconfig
