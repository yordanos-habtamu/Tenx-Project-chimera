# Project Chimera - Technical Specifications

## API Contracts

### Supervisor Agent API

**POST /api/v1/supervisor/task**
```json
{
  "task_id": "string (UUID)",
  "task_type": "enum(coordinate_content_creation|analyze_trends|publish_content|register_subagent)",
  "priority": "enum(low|medium|high|critical)",
  "timeout": "integer (seconds, default: 300)",
  "payload": {
    "topic": "string (optional)",
    "keywords": ["string"],
    "timeframe": "string (e.g., '7d', '30d')",
    "content_type": "enum(script|video|thumbnail|mixed)",
    "platforms": ["enum(youtube|twitter|instagram|tiktok)"]
  },
  "callback_url": "string (optional webhook endpoint)"
}
```

**Response:**
```json
{
  "task_id": "string",
  "status": "enum(queued|processing|completed|failed)",
  "created_at": "ISO8601 timestamp",
  "estimated_completion": "ISO8601 timestamp",
  "result": {
    "workflow_completed": "boolean",
    "phases": {
      "research": {"status": "string", "duration": "seconds"},
      "content": {"status": "string", "duration": "seconds"},
      "safety": {"status": "string", "duration": "seconds"},
      "distribution": {"status": "string", "duration": "seconds"}
    }
  }
}
```

### Agent Registration API

**POST /api/v1/supervisor/register**
```json
{
  "agent_id": "string",
  "agent_type": "enum(supervisor|trend_fetcher|niche_analyst|script_writer|video_generator|thumbnail_designer|content_moderation|human_in_loop|platform_publisher|openclaw_announcer)",
  "capabilities": ["string"],
  "max_concurrent_tasks": "integer",
  "health_check_endpoint": "string (URL)"
}
```

**Response:**
```json
{
  "agent_id": "string",
  "registration_status": "enum(success|failed)",
  "assigned_swarm": "enum(research|content|safety|distribution)",
  "heartbeat_interval": "integer (seconds)"
}
```

### Research Agent APIs

**POST /api/v1/research/trends**
```json
{
  "request_id": "string",
  "topics": ["string"],
  "geographic_scope": "enum(global|regional|local)",
  "time_range": {
    "start": "ISO8601 timestamp",
    "end": "ISO8601 timestamp"
  },
  "platform_filters": ["enum(youtube|twitter|google|reddit)"],
  "minimum_volume_threshold": "integer"
}
```

**Response:**
```json
{
  "request_id": "string",
  "trends": [
    {
      "keyword": "string",
      "volume": "integer",
      "trend_score": "float (0-100)",
      "velocity": "float (growth rate)",
      "related_terms": ["string"],
      "platform_breakdown": {
        "youtube": {"volume": "integer", "engagement": "float"},
        "twitter": {"volume": "integer", "engagement": "float"}
      }
    }
  ],
  "analysis_timestamp": "ISO8601 timestamp",
  "confidence_level": "float (0-1)"
}
```

### Content Generation APIs

**POST /api/v1/content/generate-script**
```json
{
  "script_id": "string",
  "research_data": {
    "trends": ["object"],
    "target_audience": {
      "demographics": "object",
      "interests": ["string"],
      "preferred_tone": "enum(informative|entertaining|educational)"
    }
  },
  "content_requirements": {
    "length_target": "enum(short|medium|long)",
    "format": "enum(monologue|dialogue|interview)",
    "call_to_action": "string (optional)"
  },
  "brand_guidelines": {
    "voice_style": "string",
    "prohibited_topics": ["string"],
    "required_elements": ["string"]
  }
}
```

**Response:**
```json
{
  "script_id": "string",
  "generated_script": "string",
  "metadata": {
    "word_count": "integer",
    "estimated_reading_time": "integer (minutes)",
    "seo_keywords_incorporated": ["string"],
    "readability_score": "float (0-100)"
  },
  "quality_metrics": {
    "engagement_prediction": "float (0-1)",
    "originality_score": "float (0-1)",
    "policy_compliance": "float (0-1)"
  }
}
```

## Database Schema

### Entity Relationship Diagram

```
agents
├── agent_id (PK)
├── agent_type
├── swarm_assignment
├── status
├── last_heartbeat
└── capabilities (JSON)

tasks
├── task_id (PK)
├── agent_id (FK)
├── task_type
├── status
├── priority
├── created_at
├── started_at
├── completed_at
└── payload (JSON)

content
├── content_id (PK)
├── task_id (FK)
├── content_type
├── title
├── body/script
├── metadata (JSON)
├── status
├── created_at
└── approved_at

research_data
├── research_id (PK)
├── task_id (FK)
├── topic
├── findings (JSON)
├── confidence_score
├── created_at
└── expires_at

analytics
├── analytic_id (PK)
├── content_id (FK)
├── platform
├── metrics (JSON)
├── collected_at
└── engagement_rate

compliance_records
├── record_id (PK)
├── content_id (FK)
├── moderator_agent_id (FK)
├── safety_score
├── violations_found
├── human_review_required
├── approved
└── reviewed_at

platform_credentials
├── credential_id (PK)
├── platform_name
├── user_identifier
├── access_token (encrypted)
├── refresh_token (encrypted)
├── expires_at
└── scopes (JSON)
```

### Core Tables Schema

**agents table:**
```sql
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type VARCHAR(50) NOT NULL,
    swarm_assignment VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'idle',
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    capabilities JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**tasks table:**
```sql
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(agent_id),
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    payload JSONB NOT NULL,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);
```

**content table:**
```sql
CREATE TABLE content (
    content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(task_id),
    content_type VARCHAR(30) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    metadata JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    approval_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE
);
```

**indexes for performance:**
```sql
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_tasks_agent_status ON tasks(agent_id, status);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_content_created_at ON content(created_at);
```

## Agent Communication Protocol

### Message Format
```json
{
  "message_id": "UUID",
  "sender_id": "agent_id",
  "recipient_id": "agent_id or 'broadcast'",
  "message_type": "enum(task_assignment|status_update|result|heartbeat|error)",
  "payload": {},
  "timestamp": "ISO8601 timestamp",
  "correlation_id": "UUID (for tracking related messages)"
}
```

### Health Check Protocol
Agents must send heartbeat messages every 30 seconds:
```json
{
  "agent_id": "string",
  "status": "enum(healthy|degraded|unhealthy)",
  "metrics": {
    "cpu_usage": "float (0-100)",
    "memory_usage": "float (0-100)",
    "active_tasks": "integer",
    "queue_length": "integer"
  },
  "timestamp": "ISO8601 timestamp"
}
```

This technical specification provides the detailed contracts and data structures needed for implementing the Project Chimera system architecture.