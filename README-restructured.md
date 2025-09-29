# Perplexica - AI-Powered Internal Search Assistant

A restructured version of Perplexica optimized for internal usage with a frontend-backend separation architecture.

## 🏗️ Architecture

- **Frontend**: Next.js 15.2.2 + React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python + LangChain + UV Package Manager
- **Database**: PostgreSQL
- **Deployment**: Docker + Docker Compose

## 📁 Project Structure

```
Perplexica/
├── frontend/           # Next.js frontend application
│   ├── src/
│   │   ├── app/        # Next.js app router pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities and API client
│   ├── Dockerfile
│   └── package.json
├── backend/            # FastAPI backend application
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # Configuration and database
│   │   ├── models/     # Database models
│   │   └── services/   # Business logic
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml  # Multi-container orchestration
└── .env.example       # Environment variables template
```

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd Perplexica
   cp .env.example .env
   ```

2. **Configure environment variables**:
   Edit `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # ... other API keys
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Setup

#### Backend Development

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies with UV**:
   ```bash
   uv sync
   ```

3. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development server**:
   ```bash
   uv run dev
   ```

#### Frontend Development

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Supported LLM Providers

- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo, GPT-4o
- **Anthropic**: Claude 3 (Haiku, Sonnet, Opus), Claude 3.5 Sonnet
- **Google**: Gemini Pro, Gemini 1.5 Pro/Flash
- **Groq**: Llama 3.1/3.2 models
- **Custom OpenAI**: Compatible endpoints

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `GOOGLE_API_KEY` | Google AI API key | Optional |
| `GROQ_API_KEY` | Groq API key | Optional |
| `DATABASE_URL` | PostgreSQL connection URL | ✅ |
| `CUSTOM_OPENAI_API_URL` | Custom OpenAI-compatible endpoint | Optional |

## 📊 Database

The application uses PostgreSQL with the following main tables:

- **chats**: Chat sessions with metadata
- **messages**: Individual messages with role, content, and sources

Database migrations are handled automatically on startup.

## 🔌 API Endpoints

### Core Endpoints

- `GET /api/models` - Available LLM models
- `POST /api/search` - Search and chat endpoint
- `GET /api/chats` - List all chats
- `POST /api/chats` - Create new chat
- `GET /api/chats/{id}` - Get specific chat
- `DELETE /api/chats/{id}` - Delete chat
- `POST /api/uploads` - File upload
- `POST /api/suggestions` - Get response suggestions

### API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View service status
docker-compose ps
```

## 🔍 Features

### ✅ Supported Features

- **AI Chat**: Conversational AI with multiple LLM providers
- **File Upload**: Support for document processing
- **Chat History**: Persistent conversation storage
- **Model Selection**: Dynamic switching between AI models
- **Streaming Responses**: Real-time response generation
- **Focus Modes**: Writing Assistant mode for internal usage

### ❌ Removed Features (Internal Usage)

- Web search capabilities
- Image search
- Video search
- News discovery
- SearxNG integration

## 🛠️ Development

### Adding New LLM Providers

1. Add provider configuration in `backend/app/services/llm/providers.py`
2. Update model lists in `get_available_models()`
3. Test provider integration

### Frontend API Integration

The frontend uses a centralized API client (`src/lib/api.ts`) for all backend communication:

```typescript
import { apiClient } from '@/lib/api'

// Example usage
const response = await apiClient.post('/api/search', {
  query: 'Hello',
  focusMode: 'writingAssistant'
})
```

## 📝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure PostgreSQL is running
   - Check `DATABASE_URL` in environment variables
   - Verify PostgreSQL credentials

2. **API Key Errors**:
   - Verify API keys are correctly set in `.env`
   - Check API key permissions and quotas

3. **Docker Issues**:
   - Run `docker-compose down` and `docker-compose up -d --build`
   - Check Docker logs: `docker-compose logs backend`

4. **Frontend Build Errors**:
   - Clear Next.js cache: `rm -rf .next`
   - Reinstall dependencies: `rm -rf node_modules && npm install`