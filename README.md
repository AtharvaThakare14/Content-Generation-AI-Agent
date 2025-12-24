# Course Generation AI Agent

An intelligent AI-powered system for automatically generating comprehensive educational courses, modules, and lessons using advanced language models and graph-based workflows.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [AI Agents & Workflows](#ai-agents--workflows)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Course Generation AI Agent is a sophisticated system that leverages OpenAI's GPT models and LangGraph to automatically create structured educational content. It generates:

- **Course Descriptions**: Concise, compelling course descriptions
- **Modules**: Organized learning modules with clear objectives
- **Lessons**: Detailed lesson content with theory and practical exercises
- **Quality Assurance**: Built-in quality checking and improvement mechanisms

The system supports multiple difficulty levels (Basic, Intermediate, Advanced) and can generate age-appropriate content for different learner groups (e.g., kids aged 11-16).

## ✨ Features

- 🤖 **AI-Powered Course Generation**: Automatically generates complete course structures using OpenAI GPT models
- 📚 **Multi-Level Content**: Supports Basic, Intermediate, and Advanced difficulty levels
- 🎓 **Structured Learning Paths**: Creates organized modules and lessons with clear learning objectives
- 🔍 **Quality Assurance**: Built-in quality checking and content improvement mechanisms
- 💬 **Interactive Chatbot**: Context-aware lesson chatbot for student assistance
- 🗂️ **Domain & Segment Management**: Organize courses by domains and segments
- 🔗 **Combined Courses**: Merge multiple courses into comprehensive learning paths
- 📊 **MongoDB Integration**: Efficient data storage and retrieval
- 🚀 **Serverless Ready**: Optimized for serverless deployments (Vercel, Railway)

## 🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Application]
        API_CLIENT[API Clients]
    end

    subgraph "API Layer"
        FASTAPI[FastAPI Application]
        ROUTER[API Router]
        CORS[CORS Middleware]
    end

    subgraph "Business Logic Layer"
        COMPONENTS[Components Layer]
        COURSES[Courses Component]
        DOMAINS[Domains Component]
        MODULES[Modules Component]
        LESSONS[Lessons Component]
        SEGMENTS[Segments Component]
        COMBINED[Combined Courses]
    end

    subgraph "AI Agents Layer"
        LANGGRAPH[LangGraph Workflows]
        
        subgraph "Course Generation Pipeline"
            DESC_GEN[Course Description Generator]
            MODULE_GEN[Module Generator]
            LESSON_GEN[Lessons Generator]
            QUALITY[Quality Checker]
        end
        
        CHATBOT[Lesson Chatbot]
    end

    subgraph "Data Layer"
        MONGO[(MongoDB)]
        SUPABASE[(Supabase)]
    end

    subgraph "External Services"
        OPENAI[OpenAI API]
    end

    WEB --> FASTAPI
    API_CLIENT --> FASTAPI
    FASTAPI --> ROUTER
    ROUTER --> CORS
    ROUTER --> COMPONENTS
    
    COMPONENTS --> COURSES
    COMPONENTS --> DOMAINS
    COMPONENTS --> MODULES
    COMPONENTS --> LESSONS
    COMPONENTS --> SEGMENTS
    COMPONENTS --> COMBINED
    
    COURSES --> DESC_GEN
    COURSES --> MODULE_GEN
    COURSES --> LESSON_GEN
    
    DESC_GEN --> QUALITY
    MODULE_GEN --> LANGGRAPH
    LESSON_GEN --> LANGGRAPH
    LESSON_GEN --> QUALITY
    
    LANGGRAPH --> OPENAI
    CHATBOT --> OPENAI
    
    COMPONENTS --> MONGO
    COMPONENTS --> SUPABASE
```

### Course Generation Workflow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant CourseComponent
    participant DescGenerator
    participant ModuleGenerator
    participant LessonGenerator
    participant QualityChecker
    participant MongoDB
    participant OpenAI

    Client->>API: POST /api/v1/courses/ai/add-course
    API->>CourseComponent: generate_course(data)
    
    CourseComponent->>DescGenerator: generate_description(data, course_id)
    DescGenerator->>OpenAI: Generate course description
    OpenAI-->>DescGenerator: Description text
    DescGenerator->>QualityChecker: check_description_quality()
    QualityChecker-->>DescGenerator: Quality report
    DescGenerator->>MongoDB: Save course document
    DescGenerator-->>CourseComponent: Course document
    
    CourseComponent->>ModuleGenerator: generate_module(course_data)
    ModuleGenerator->>OpenAI: Generate modules structure
    OpenAI-->>ModuleGenerator: Modules JSON
    ModuleGenerator->>MongoDB: Save modules
    ModuleGenerator-->>CourseComponent: Modules data
    
    CourseComponent->>LessonGenerator: generate_lessons_for_each_module(modules, course_id)
    
    loop For each module
        LessonGenerator->>OpenAI: Generate lesson outlines
        OpenAI-->>LessonGenerator: Lesson outlines
        
        loop For each lesson
            LessonGenerator->>OpenAI: Expand lesson content
            OpenAI-->>LessonGenerator: Detailed content
            LessonGenerator->>QualityChecker: check_lesson_quality()
            QualityChecker-->>LessonGenerator: Quality report
        end
    end
    
    LessonGenerator->>MongoDB: Save lessons
    LessonGenerator-->>CourseComponent: Complete course data
    CourseComponent-->>API: Success response
    API-->>Client: Course generated successfully
```

### Component Interaction Flow

```mermaid
graph LR
    subgraph "Request Flow"
        A[API Endpoint] --> B[Component]
        B --> C{AI Generation?}
        C -->|Yes| D[AI Agent]
        C -->|No| E[Database Operation]
        D --> F[OpenAI API]
        F --> D
        D --> G[Quality Check]
        G --> H[Save to MongoDB]
        E --> H
        H --> I[Response]
    end
```

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.10+**: Primary programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications

### AI & ML
- **LangChain**: Framework for building LLM applications
- **LangGraph**: State machine framework for multi-agent workflows
- **OpenAI GPT Models**: For content generation (via LangChain)

### Database
- **MongoDB**: NoSQL database for storing courses, modules, lessons
- **PyMongo**: MongoDB driver for Python

### Authentication & Services
- **Supabase**: Backend-as-a-Service for authentication and additional features
- **Python-JOSE**: JWT token handling
- **Passlib**: Password hashing

### Deployment
- **Docker**: Containerization
- **Vercel**: Serverless deployment platform
- **Railway**: Alternative deployment platform

## 📁 Project Structure

```
Course-Generation-AI-Agent/
├── api/
│   └── index.py                 # Vercel serverless entry point
├── src/
│   ├── ai/                      # AI agents and workflows
│   │   ├── course_description_generator/
│   │   │   ├── course_description.py
│   │   │   └── states/
│   │   ├── course_generation/
│   │   │   ├── agents/
│   │   │   │   ├── course_module_generator.py
│   │   │   │   └── lesson_content_generator.py
│   │   │   ├── agent_states/
│   │   │   ├── graph.py
│   │   │   └── insertion/
│   │   ├── domain_description_generator/
│   │   ├── lesson_chatbot/
│   │   │   └── lesson_chatbot.py
│   │   ├── lessons_generator/
│   │   │   ├── agents/
│   │   │   │   ├── lessons_generator.py
│   │   │   │   └── lesson_quality_checker.py
│   │   │   └── states/
│   │   └── module_generator/
│   │       ├── agents/
│   │       ├── graph.py
│   │       └── states/
│   ├── api/                      # API routes
│   │   ├── api_router.py
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── courses.py
│   │           ├── domains.py
│   │           ├── modules.py
│   │           ├── lessons.py
│   │           ├── segments.py
│   │           └── auth.py
│   ├── components/               # Business logic components
│   │   ├── courses.py
│   │   ├── domains.py
│   │   ├── modules.py
│   │   ├── lessons.py
│   │   ├── segments.py
│   │   └── combined_courses.py
│   ├── configurations/           # Service configurations
│   │   ├── mongodb.py
│   │   ├── openai.py
│   │   └── supabase.py
│   ├── constants/                # Constants and configuration
│   │   ├── mongodb.py
│   │   ├── openai.py
│   │   └── supabase.py
│   ├── db/                       # Database utilities
│   │   ├── mongodb_singleton.py
│   │   └── create_tables.sql
│   ├── schemas/                  # Pydantic models
│   │   ├── courses.py
│   │   ├── domains.py
│   │   ├── modules.py
│   │   ├── lessons.py
│   │   ├── segments.py
│   │   └── combined_courses.py
│   ├── utils/                    # Utility functions
│   │   ├── unique_id_generator.py
│   │   ├── mongo_insert_one.py
│   │   ├── auth.py
│   │   └── add_new_field_dict.py
│   ├── logging.py               # Logging configuration
│   └── exception.py              # Custom exception handling
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── vercel.json                   # Vercel deployment config
├── railway.json                  # Railway deployment config
└── README.md                     # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- MongoDB Atlas account (or local MongoDB instance)
- OpenAI API key
- Supabase account (optional, for authentication)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Course-Generation-AI-Agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_connection_string
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8080`

## ⚙️ Configuration

### MongoDB Configuration

Update `src/constants/mongodb.py` with your MongoDB connection details:

```python
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/..."
AI_TUTOR_IQAN_DATABASE_NAME = "Ai-Tutor-iqan"
```

### OpenAI Configuration

Set your OpenAI API key in environment variables or update `src/constants/openai.py`:

```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### Supabase Configuration

Configure Supabase credentials in `src/constants/supabase.py`:

```python
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

## 📡 API Endpoints

### Courses

#### Generate Course with AI
```http
POST /api/v1/courses/ai/add-course
Content-Type: application/json

{
  "course_name": "Python Programming",
  "level": "intermediate",
  "image_uri": "https://example.com/image.jpg",
  "description": "Learn Python from scratch"
}
```

#### Get All Courses
```http
GET /api/v1/courses/get-courses
```

#### Get Courses by Segment
```http
GET /api/v1/courses/get-courses-by-segments?segment_id=SEGMENT_ID
```

#### Update Course
```http
PUT /api/v1/courses/update-courses
Content-Type: application/json

{
  "course_id": "COURSE_ID",
  "course_name": "Updated Name",
  "level": "advanced",
  "image_uri": "https://example.com/new-image.jpg",
  "description": "Updated description"
}
```

#### Delete Course
```http
DELETE /api/v1/courses/delete-courses
Content-Type: application/json

{
  "course_id": "COURSE_ID"
}
```

#### Combine Courses
```http
POST /api/v1/courses/combine-courses
Content-Type: application/json

{
  "course_name": "Full Stack Development",
  "course_ids": ["COURSE_ID_1", "COURSE_ID_2"]
}
```

### Domains

#### Add Domain
```http
POST /api/v1/domain/add-domain
Content-Type: application/json

{
  "domain_name": "Web Development",
  "description": "Learn web development technologies"
}
```

#### Get All Domains
```http
GET /api/v1/domain/get-domains
```

### Modules

#### Get Modules
```http
GET /api/v1/modules/get-modules?course_id=COURSE_ID
```

#### Update Module
```http
PUT /api/v1/modules/update/module
Content-Type: application/json

{
  "module_id": "MODULE_ID",
  "title": "Updated Title",
  "description": "Updated description"
}
```

### Lessons

#### Get Lessons
```http
GET /api/v1/lessons/get-lessons?course_id=COURSE_ID&module_id=MODULE_ID
```

#### Lesson Chatbot
```http
POST /api/v1/lessons/ai/bot
Content-Type: application/json

{
  "context": "Lesson content about Python lists...",
  "question": "What are Python lists?"
}
```

### Segments

#### Add Segment
```http
POST /api/v1/segments/add-segments
Content-Type: application/json

{
  "segment_name": "Programming",
  "description": "Programming related courses"
}
```

#### Get All Segments
```http
GET /api/v1/segments/get-all-segments
```

## 🤖 AI Agents & Workflows

### Course Description Generator

Generates concise, compelling course descriptions (1-2 sentences, 15-50 words).

**Features:**
- Quality checking and improvement
- Marketing-oriented language
- Technology-specific content

**Location:** `src/ai/course_description_generator/`

### Module Generator

Creates structured learning modules with:
- Module titles and descriptions
- Learning objectives
- Number of lessons
- Lesson outlines

**Features:**
- Age-appropriate content for different levels
- Sequential progression from beginner to advanced
- Comprehensive topic coverage

**Location:** `src/ai/module_generator/`

### Lessons Generator

Generates detailed lesson content with two-phase approach:

1. **Outline Generation**: Creates lesson structure and outlines
2. **Content Expansion**: Expands outlines into comprehensive content

**Features:**
- Two lesson types: "read" (theory) and "read_and_execute" (hands-on)
- Detailed instructional content (2000-3000 words)
- Coding exercises with solutions
- Quality checking and improvement
- Markdown formatting for frontend rendering

**Location:** `src/ai/lessons_generator/`

### Quality Checker

Ensures content quality through:
- Description quality assessment
- Lesson content evaluation
- Automatic content improvement
- Quality scoring (0-100)

**Location:** `src/ai/lessons_generator/agents/lesson_quality_checker.py`

### Lesson Chatbot

Context-aware chatbot that answers questions based on lesson content.

**Features:**
- Context-bound responses
- Topic relevance checking
- Friendly greetings and guidance

**Location:** `src/ai/lesson_chatbot/`

## 🗄️ Database Schema

### MongoDB Collections

#### Courses Collection
```javascript
{
  "course_id": "COURSE_XXX",
  "course_name": "Python Programming",
  "level": "intermediate",
  "description": "Learn Python...",
  "image_uri": "https://...",
  "created_at": ISODate("2024-01-01"),
  "is_popular": false,
  "is_trending": false,
  "segment_ids": ["SEGMENT_XXX"]
}
```

#### Modules Collection
```javascript
{
  "course_id": "COURSE_XXX",
  "level": "intermediate",
  "modules": [
    {
      "module_id": "MODULE_XXX",
      "title": "Introduction to Python",
      "description": "...",
      "learning_objectives": ["..."],
      "number_of_lessons": 5
    }
  ]
}
```

#### Lessons Collection
```javascript
{
  "course_id": "COURSE_XXX",
  "modules": [
    {
      "module_id": "MODULE_XXX",
      "lessons": [
        {
          "lesson_id": "LESSON_XXX",
          "title": "Python Basics",
          "type": "read",
          "content": "## Introduction\n...",
          "instruction": "...",
          "expected_output": "...",
          "answer": "..."
        }
      ]
    }
  ]
}
```

#### Domains Collection
```javascript
{
  "domain_id": "DOMAIN_XXX",
  "domain_name": "Web Development",
  "description": "...",
  "courses_ids": ["COURSE_XXX"],
  "segment_ids": ["SEGMENT_XXX"]
}
```

#### Segments Collection
```javascript
{
  "segment_id": "SEGMENT_XXX",
  "segment_name": "Programming",
  "description": "..."
}
```

#### Combined Courses Collection
```javascript
{
  "combined_course_id": "COMBINED_XXX",
  "course_name": "Full Stack Development",
  "course_ids": ["COURSE_XXX", "COURSE_YYY"],
  "is_trending": false,
  "is_popular": false
}
```

## 🚢 Deployment

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t course-generation-ai .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 --env-file .env course-generation-ai
   ```

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

   The `vercel.json` configuration handles serverless function routing.

### Railway Deployment

1. **Connect your repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push**

## 💡 Usage Examples

### Generate a Complete Course

```python
import requests

# Generate a course
response = requests.post(
    "http://localhost:8080/api/v1/courses/ai/add-course",
    json={
        "course_name": "Machine Learning Fundamentals",
        "level": "intermediate",
        "image_uri": "https://example.com/ml.jpg",
        "description": "Learn the fundamentals of machine learning"
    }
)

course_data = response.json()
print(f"Course ID: {course_data['course_id']}")
```

### Query Lesson Chatbot

```python
response = requests.post(
    "http://localhost:8080/api/v1/lessons/ai/bot",
    json={
        "context": "Python lists are ordered collections of items...",
        "question": "How do I add items to a list?"
    }
)

answer = response.json()
print(answer['response'])
```

### Get Course Structure

```python
# Get all courses
courses = requests.get("http://localhost:8080/api/v1/courses/get-courses").json()

# Get modules for a course
modules = requests.get(
    "http://localhost:8080/api/v1/modules/get-modules",
    params={"course_id": "COURSE_XXX"}
).json()

# Get lessons for a module
lessons = requests.get(
    "http://localhost:8080/api/v1/lessons/get-lessons",
    params={"course_id": "COURSE_XXX", "module_id": "MODULE_XXX"}
).json()
```

## 🔧 Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Logging

Logs are stored in the `tmp/` directory with timestamp-based filenames.

### Testing

```bash
# Run tests (if available)
pytest tests/
```

## 📝 Notes

- The system uses a MongoDB singleton pattern optimized for serverless environments
- Content generation can take several minutes for complex courses
- Quality checking adds additional processing time but ensures high-quality output
- The system supports both user-provided and AI-generated descriptions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🔗 Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [MongoDB Documentation](https://docs.mongodb.com/)

## 📧 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using FastAPI, LangChain, and OpenAI**
