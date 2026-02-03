# 🧠 RAG-DocuMind

> AI-Powered Technical Documentation Assistant - Search and chat with your docs using local LLMs

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DocuMind transforms your technical documentation into an intelligent assistant. Upload your docs, READMEs, code files, and PDFs, then ask questions in natural language. Powered by local LLMs via Ollama, it's completely free and runs on your machine.

![DocuMind Demo](https://via.placeholder.com/800x450?text=DocuMind+Demo+Screenshot)

## ✨ Features

- 📁 **Multi-Format Support** - Upload Markdown, PDF, Python, JavaScript, TypeScript, Java, and more
- 🔍 **Semantic Search** - Find relevant information using AI-powered embeddings
- 💬 **Conversational Q&A** - Ask questions and get answers with source citations
- 🏃 **100% Local** - Runs entirely on your machine using Ollama (no API costs!)
- 🎯 **Code-Aware** - Intelligent chunking preserves function/class boundaries
- 📊 **Source Citations** - Every answer includes references to original documents
- ⚡ **Fast & Efficient** - Optimized for Apple Silicon (M1/M2/M3)
- 🎨 **Beautiful UI** - Modern, responsive interface built with React & Tailwind

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- [Ollama](https://ollama.ai/) installed

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/documind.git
cd documind/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p app/routers app/services app/models
touch app/__init__.py app/routers/__init__.py app/services/__init__.py app/models/__init__.py

# Create .env file
cat > .env << EOF
CHROMA_PERSIST_DIRECTORY=./chroma_db
UPLOAD_DIRECTORY=./uploads
MAX_FILE_SIZE=10485760
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EOF

# Start Ollama and pull the model
ollama serve  # In a separate terminal
ollama pull llama3.2:3b

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### Frontend Setup

```bash
# Navigate to frontend directory
cd documind/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`.

## 📖 Usage

### 1. Upload Documents

Navigate to the **Upload** tab and drag & drop your files or click to browse. Supported formats:

- Documentation: `.md`, `.txt`, `.pdf`
- Code: `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.java`, `.go`, `.rs`, `.cpp`, `.c`, `.h`

### 2. Search Your Docs

Use the **Search** tab to perform semantic searches:

```
Query: "how to configure database"
Results: Relevant chunks from your docs with similarity scores
```

### 3. Ask Questions

Switch to the **Ask Questions** tab for conversational Q&A:

```
You: "What are the installation steps?"
DocuMind: "Based on the documentation, here are the installation steps:
1. Clone the repository
2. Install dependencies with pip install -r requirements.txt
3. ...

Sources: README.md (chunk 2), INSTALL.md (chunk 0)"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│  Upload Interface │ Search UI │ Chat Interface          │
└───────────────────┬─────────────────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│                                                          │
│  ┌────────────┐  ┌──────────┐  ┌─────────────────────┐│
│  │  Document  │  │  Search  │  │  Ollama Integration ││
│  │  Ingestion │  │  Service │  │   (LLM Responses)   ││
│  └────────────┘  └──────────┘  └─────────────────────┘│
│         │              │                    │           │
└─────────┼──────────────┼────────────────────┼───────────┘
          │              │                    │
     ┌────▼────┐    ┌───▼────┐        ┌─────▼──────┐
     │  File   │    │ Vector │        │   Ollama   │
     │ Storage │    │   DB   │        │  (llama3)  │
     └─────────┘    │(Chroma)│        └────────────┘
                    └────────┘
```

### Key Components

**Backend Services:**
- `file_processor.py` - Handles file reading and type detection
- `chunking.py` - Intelligent document splitting (code-aware)
- `embedding.py` - Generates vector embeddings
- `vectorstore.py` - ChromaDB operations
- `ollama_service.py` - LLM integration
- `search_service.py` - Semantic search and Q&A

**Frontend Components:**
- Upload interface with drag & drop
- Semantic search with relevance scoring
- Conversational chat with message history
- Real-time statistics dashboard

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Storage paths
CHROMA_PERSIST_DIRECTORY=./chroma_db
UPLOAD_DIRECTORY=./uploads

# File upload limits
MAX_FILE_SIZE=10485760  # 10MB

# Embedding configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Chunking strategy
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Ollama Models

DocuMind supports any Ollama model. Try different ones:

```bash
# Default (fast, efficient)
ollama pull llama3.2:3b

# More powerful
ollama pull mistral:7b
ollama pull llama3:8b

# Code-focused
ollama pull codellama:7b
```

Update the model in `app/services/ollama_service.py`:

```python
def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:7b"):
```

## 📊 API Documentation

### Document Endpoints

**Upload Document**
```http
POST /documents/upload
Content-Type: multipart/form-data

file: <file>
```

**Get Statistics**
```http
GET /documents/stats
```

### Search Endpoints

**Semantic Search**
```http
POST /search/semantic
Content-Type: application/json

{
  "query": "your search query",
  "top_k": 5,
  "filters": {}
}
```

**Ask Question (with LLM)**
```http
POST /search/ask
Content-Type: application/json

{
  "query": "your question",
  "top_k": 5,
  "conversation_history": []
}
```

**Health Check**
```http
GET /search/health
```

Full API documentation available at `http://localhost:8000/docs` when running.

## 🧪 Testing

### Backend Tests

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

### Frontend Tests

```bash
# Run tests
npm test

# E2E tests
npm run test:e2e
```

## 🚢 Deployment

### Backend (Railway)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up
```

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd documind-frontend
vercel
```

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t documind-backend .
docker run -p 8000:8000 documind-backend
```

## 🎯 Roadmap

- [ ] Multi-user support with authentication
- [ ] GitHub integration (auto-index repositories)
- [ ] Slack integration (search from Slack)
- [ ] Web scraping for documentation sites
- [ ] Custom model fine-tuning
- [ ] Export conversations
- [ ] API rate limiting
- [ ] Advanced analytics dashboard
- [ ] Notion integration
- [ ] Confluence integration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate tests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM runtime
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [LangChain](https://www.langchain.com/) - LLM orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Sentence Transformers](https://www.sbert.net/) - Embedding models

## 💬 Support

- 📫 Email: harshrs641@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/harshrs641/documind/issues)
- 💼 LinkedIn: [Your LinkedIn](https://www.linkedin.com/in/harsh-flutter-web3/)
- 🌐 Website: [https://bento.me/harsh-web3](https://bento.me/harsh-web3)

---

Built with ❤️ by [Harsh Raj Singh](https://github.com/harshrs641)

**⭐ Star this repo if you find it helpful!**