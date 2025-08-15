@minLength(1)
@maxLength(50)
@description('The API Management service name')
param name string

@description('The location for the Azure API Management service')
param location string = resourceGroup().location

@description('Resource tags')
param tags object = {}

@description('The publisher name for the API Management service')
param publisherName string

@description('The publisher email for the API Management service')
param publisherEmail string

@description('The SKU for the API Management service')
@allowed(['Developer', 'Standard', 'Premium'])
param sku string = 'Developer'

@description('The number of scale units for the API Management service')
param skuCount int = 1

@description('The backend API URI')
param backendApiUri string

// Create API Management service
resource apiManagement 'Microsoft.ApiManagement/service@2023-05-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
    capacity: skuCount
  }
  properties: {
    publisherName: publisherName
    publisherEmail: publisherEmail
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Note: Application Insights logger removed to simplify deployment

// Create the AI Agent API
resource aiAgentApi 'Microsoft.ApiManagement/service/apis@2023-05-01-preview' = {
  parent: apiManagement
  name: 'ai-agent-api-final'
  properties: {
    displayName: 'AI Agent API Final'
    description: 'Final API for AI Agent functionality'
    path: 'aiagent'
    protocols: ['https']
    serviceUrl: backendApiUri
    subscriptionRequired: true
  }
}

// Health check operation
resource healthOperation 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: aiAgentApi
  name: 'health-check'
  properties: {
    displayName: 'Health Check'
    method: 'GET'
    urlTemplate: '/health'
    description: 'Health check endpoint'
  }
}

// Agent search operation
resource agentSearchOperation 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: aiAgentApi
  name: 'agent-search'
  properties: {
    displayName: 'Agent Search'
    method: 'POST'
    urlTemplate: '/agent/search'
    description: 'Search operation for the AI agent'
    request: {
      queryParameters: []
      headers: []
      representations: [
        {
          contentType: 'application/json'
        }
      ]
    }
    responses: [
      {
        statusCode: 200
        description: 'Successful response'
        representations: [
          {
            contentType: 'application/json'
          }
        ]
      }
    ]
  }
}

// Chat operation
resource chatOperation 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: aiAgentApi
  name: 'chat'
  properties: {
    displayName: 'Chat'
    method: 'POST'
    urlTemplate: '/chat'
    description: 'Chat endpoint for the AI agent'
    request: {
      queryParameters: []
      headers: []
      representations: [
        {
          contentType: 'application/json'
        }
      ]
    }
    responses: [
      {
        statusCode: 200
        description: 'Successful response'
        representations: [
          {
            contentType: 'application/json'
          }
        ]
      }
    ]
  }
}

// Create CORS policy for the API
resource corsPolicy 'Microsoft.ApiManagement/service/apis/policies@2023-05-01-preview' = {
  parent: aiAgentApi
  name: 'policy'
  properties: {
    value: '''
<policies>
  <inbound>
    <base />
    <cors>
      <allowed-origins>
        <origin>*</origin>
      </allowed-origins>
      <allowed-methods>
        <method>GET</method>
        <method>POST</method>
        <method>PUT</method>
        <method>DELETE</method>
        <method>OPTIONS</method>
      </allowed-methods>
      <allowed-headers>
        <header>*</header>
      </allowed-headers>
    </cors>
    <rate-limit calls="100" renewal-period="60" remaining-calls-variable-name="remainingCallsPerMinute" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
    '''
    format: 'xml'
  }
}

// Create a product for the API
resource aiAgentProduct 'Microsoft.ApiManagement/service/products@2023-05-01-preview' = {
  parent: apiManagement
  name: 'ai-agent-product-final'
  properties: {
    displayName: 'AI Agent Product Final'
    description: 'Final product for AI Agent API access'
    subscriptionRequired: true
    approvalRequired: false
    state: 'published'
  }
}

// Add API to product
resource productApi 'Microsoft.ApiManagement/service/products/apis@2023-05-01-preview' = {
  parent: aiAgentProduct
  name: aiAgentApi.name
}

// Create quota policy for the product
resource quotaPolicy 'Microsoft.ApiManagement/service/products/policies@2023-05-01-preview' = {
  parent: aiAgentProduct
  name: 'policy'
  properties: {
    value: '''
<policies>
  <inbound>
    <base />
    <quota calls="1000" renewal-period="3600" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
    '''
    format: 'xml'
  }
}

// Create a default subscription
resource defaultSubscription 'Microsoft.ApiManagement/service/subscriptions@2023-05-01-preview' = {
  parent: apiManagement
  name: 'default-subscription-final'
  properties: {
    displayName: 'Default Subscription Final'
    state: 'active'
    scope: '/products/${aiAgentProduct.name}'
  }
}

// Outputs
output name string = apiManagement.name
output gateway_url string = apiManagement.properties.gatewayUrl
output management_url string = apiManagement.properties.managementApiUrl ?? ''
output portal_url string = apiManagement.properties.portalUrl ?? ''
output developer_portal_url string = apiManagement.properties.developerPortalUrl ?? ''
output subscription_id string = defaultSubscription.name
output product_id string = aiAgentProduct.name
output api_id string = aiAgentApi.name
