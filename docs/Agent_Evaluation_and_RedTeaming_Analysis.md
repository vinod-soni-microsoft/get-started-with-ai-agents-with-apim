# 🔬 Agent Evaluation & Testing and 🛡️ AI Red Teaming Analysis

## Overview

This repository includes comprehensive **Agent Evaluation & Testing** and **AI Red Teaming** capabilities that provide automated security and safety scanning to assess risk posture before production deployment. Here's a detailed analysis of these features:

---

## 🔬 Agent Evaluation & Testing Module

### **Location**: `/evals/` directory

### **Core Components**:

#### 1. **Main Evaluation Script** (`evaluate.py`)
- **Purpose**: Comprehensive agent performance evaluation using Azure AI Evaluation SDK
- **Key Features**:
  - **Multiple Evaluators**: Tool call accuracy, intent resolution, task adherence, code vulnerability, content safety, indirect attack detection
  - **Performance Metrics**: Response time, token usage, completion tracking
  - **Thread Management**: Isolated conversations for each test query
  - **Results Export**: Both local JSON files and Azure AI Foundry integration

#### 2. **Test Data** (`eval-queries.json`)
- Contains standardized test queries like:
  - "What features do the SmartView Glasses have?"
  - "How long is the warranty on the SmartView Glasses?"

#### 3. **Evaluation Configuration** (`eval-action-data-path.json`)
- Defines evaluator types: Intent Resolution, Task Adherence, Coherence, Relevance, Fluency, Violence, Sexual content evaluators

### **Evaluation Types Performed**:

1. **Operational Metrics**
   - Server run duration
   - Client run duration 
   - Token consumption (prompt + completion)
   - Ground truth comparison

2. **Quality Evaluators**
   - **Tool Call Accuracy**: Measures correct function/tool usage
   - **Intent Resolution**: Evaluates understanding of user intent
   - **Task Adherence**: Checks if agent follows instructions properly

3. **Safety Evaluators**
   - **Code Vulnerability**: Scans for security issues in generated code
   - **Content Safety**: Detects inappropriate content (violence, hate speech)
   - **Indirect Attack**: Identifies potential prompt injection vulnerabilities

### **Integration Points**:
- **Local Development**: Run evaluations during development
- **Continuous Monitoring**: Automatic evaluation after each conversation
- **CI/CD Pipeline**: GitHub Actions integration for automated testing

---

## 🛡️ AI Red Teaming Module

### **Location**: `/airedteaming/` directory

### **Core Component**: `ai_redteaming.py`

### **Purpose**: 
Automated adversarial testing to identify security vulnerabilities and safety risks in the AI agent before production deployment.

### **Key Features**:

#### 1. **Attack Strategies**
- **Flip Strategy**: Tests how the agent responds to contradictory or misleading inputs
- **Extensible Framework**: Can be configured for multiple attack vectors

#### 2. **Risk Categories**
- **Violence**: Tests for violent content generation
- **Configurable**: Can test for other risk categories (hate speech, self-harm, etc.)

#### 3. **Automated Scanning**
- **No Manual Input Required**: Automatically generates adversarial prompts
- **Agent Callback Integration**: Tests the actual deployed agent through the same interface users access
- **Results Directory**: Outputs detailed scan results to `redteam_outputs/`

#### 4. **Azure Integration**
- Uses **Azure AI Risk and Safety Evaluations**
- Leverages **Azure AI Project Client** for agent interaction
- Seamless integration with existing agent deployment

### **Security Assessment Capabilities**:

1. **Prompt Injection Testing**: Attempts to manipulate agent behavior
2. **Content Safety Validation**: Ensures agent doesn't generate harmful content
3. **Behavioral Analysis**: Tests agent's resistance to adversarial inputs
4. **Risk Scoring**: Provides quantified risk assessment

---

## 📊 Interfaces and Reports

### **1. Evaluation Results Interface**

The evaluation system provides multiple output formats:

#### **Console Output**:
```
====================================
        Evaluation Results
====================================
Metric                     | Value
---------------------------+-------
tool_call_accuracy        | 0.85
intent_resolution          | 0.92
task_adherence            | 0.88
content_safety            | 1.00
server-run-duration       | 2.45
completion-tokens         | 150
====================================
```

#### **JSON Reports**:
- **Input File**: `eval-input.jsonl` - Test data with operational metrics
- **Output File**: `eval-output.json` - Detailed evaluation results
- **Azure AI Foundry**: Web interface for visualization and tracking

### **2. Red Team Scan Reports**

#### **Directory Structure**:
```
redteam_outputs/
├── Agent-Scan_summary.json          # High-level scan results
├── Agent-Scan_conversations.json    # Detailed attack conversations
├── Agent-Scan_metrics.json          # Risk scoring and statistics
└── Agent-Scan_recommendations.json  # Security improvement suggestions
```

#### **Web Interface**:
- **Azure AI Foundry**: Integrated red team results viewer
- **Risk Dashboard**: Visual representation of security posture
- **Attack Analysis**: Detailed breakdown of successful/failed attacks

### **3. Monitoring Dashboards**

#### **Application Insights Integration**:
- **Real-time Evaluation Metrics**: Performance tracking during production
- **KQL Queries**: Custom queries for evaluation analysis
- **Alerting**: Automated notifications for evaluation failures

#### **Azure AI Foundry Tracing**:
- **Conversation Tracing**: Full request/response tracking
- **Evaluation Timeline**: Historical evaluation performance
- **Agent Performance Metrics**: Trend analysis and comparison

---

## 🚀 How to Use These Features

### **Running Agent Evaluation**:

```bash
# Install dependencies
python -m pip install -r src/requirements.txt
python -m pip install azure-ai-evaluation

# Run evaluation
python evals/evaluate.py
```

### **Running Red Team Scan**:

```bash
# Install red team dependencies
python -m pip install azure-ai-evaluation[redteam]

# Run red team scan
python airedteaming/ai_redteaming.py
```

### **Environment Variables Required**:
- `AZURE_EXISTING_AIPROJECT_ENDPOINT`: Your AI Project endpoint
- `AZURE_EXISTING_AGENT_ID` or `AZURE_AI_AGENT_NAME`: Agent identifier
- `AZURE_AI_AGENT_DEPLOYMENT_NAME`: Model deployment name

---

## 🎯 Benefits for Production Deployment

### **Risk Mitigation**:
1. **Pre-deployment Testing**: Catch security issues before going live
2. **Automated Scanning**: No manual security testing required
3. **Comprehensive Coverage**: Tests multiple attack vectors and risk categories

### **Quality Assurance**:
1. **Performance Validation**: Ensure agent meets quality thresholds
2. **Regression Testing**: Detect performance degradation over time
3. **Compliance Verification**: Meet security and safety requirements

### **Continuous Improvement**:
1. **Feedback Loop**: Regular evaluation drives improvements
2. **Benchmarking**: Compare different agent versions
3. **Risk Monitoring**: Ongoing security posture assessment

---

## 🔗 Integration with APIM Solution

These evaluation and red teaming capabilities integrate seamlessly with your APIM architecture:

1. **Testing Through APIM**: Both modules can test the agent through the APIM gateway
2. **Rate Limiting Validation**: Evaluation tests respect APIM rate limits
3. **Authentication Testing**: Security scans validate subscription key handling
4. **End-to-End Validation**: Complete request flow testing from client to AI response

This provides a comprehensive security and quality assurance framework for your enterprise AI agent solution before and after production deployment.
