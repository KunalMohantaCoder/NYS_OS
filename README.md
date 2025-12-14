# NyxOS AI Engine

Neural network-based LLM and personal assistant for NyxOS.

## Features

- **Transformer-based LLM**: Small-scale transformer model (~5-10M parameters) trained from scratch
- **BPE Tokenizer**: Custom byte-pair encoding tokenizer
- **Text Generation**: Multiple decoding strategies (greedy, beam search, sampling)
- **Personal Assistant**: Intent recognition and task execution
  - File operations (create, read, delete, list, search)
  - Folder management
  - System commands (safe execution)
  - Scheduling and calendar
- **REST API**: FastAPI service with WebSocket support
- **Integration**: Seamlessly integrated with NyxOS Java backend and React frontend

## Architecture

```
ai-engine/
├── model/              # Transformer architecture
├── training/           # Training pipeline
├── inference/          # Text generation
├── assistant/          # Personal assistant
└── api/                # API service
```

## Setup

### Prerequisites

- Python 3.9+
- PyTorch (CPU or GPU)
- pip

### Installation

1. Install dependencies:
```bash
cd ai-engine
pip install -r requirements.txt
```

### Training the Model

1. Prepare training data (optional):
   - Create `data/training/training_data.txt` with one text per line
   - The script will also use built-in assistant training data

2. Run training:
```bash
python train.py
```

Training will:
- Train a BPE tokenizer
- Create conversation pairs from training data
- Train the transformer model
- Save model and tokenizer to `data/models/`

**Note**: Training on CPU may take several hours. GPU is recommended for faster training.

## Running the AI Service

### Windows

Double-click `start_ai_service.bat` or run:
```bash
start_ai_service.bat
```

### Manual Start

```bash
cd ai-engine
python -m api.server
```

The service will start on `http://localhost:8000`

### Environment Variables

- `AI_MODEL_PATH`: Path to model file (default: `data/models/best_model.pt`)
- `AI_TOKENIZER_PATH`: Path to tokenizer (default: `data/models/tokenizer.json`)
- `AI_API_PORT`: API port (default: `8000`)
- `USE_GPU`: Use GPU if available (default: `false`)
- `ASSISTANT_BASE_PATH`: Base path for file operations
- `ASSISTANT_DATA_DIR`: Directory for assistant data

## API Endpoints

### Chat
- `POST /chat` - Generate AI response
- `POST /assistant` - Process assistant request with intent recognition
- `GET /health` - Health check
- `POST /context/clear` - Clear conversation context
- `GET /context/history` - Get conversation history

### WebSocket
- `WS /ws/chat` - Real-time chat via WebSocket

## Usage

The AI service integrates with NyxOS:

1. **Start the AI service** (see above)
2. **Start the Java backend** (from `backend/`)
3. **Start the frontend** (from `frontend/`)
4. **Open AI Assistant** from the app launcher

## Model Architecture

- **Type**: Encoder-decoder transformer
- **Parameters**: ~5-10M (configurable)
- **Embedding dimension**: 256 (default)
- **Encoder layers**: 4 (default)
- **Decoder layers**: 4 (default)
- **Attention heads**: 8 (default)
- **Feed-forward dimension**: 1024 (default)
- **Vocabulary size**: 10,000 (default)

## Personal Assistant Capabilities

The assistant can:
- **File operations**: Create, read, delete, list, search files
- **Folder management**: Create folders
- **Scheduling**: Add and manage calendar events
- **System commands**: Execute safe system commands
- **Chat**: Natural language conversation

## Security

- File operations are restricted to a base directory
- System commands are whitelisted and sanitized
- Input validation on all endpoints
- Rate limiting (can be added)

## Development

### Project Structure

- `model/`: Neural network components
- `training/`: Training pipeline and data processing
- `inference/`: Text generation and context management
- `assistant/`: Personal assistant logic
- `api/`: FastAPI service

### Adding Training Data

Add more training data to improve the model:
1. Add text files to `data/training/`
2. Or modify `train.py` to load additional datasets

### Customizing the Model

Edit `train.py` to adjust:
- Model size (d_model, num_layers)
- Vocabulary size
- Training hyperparameters
- Batch size and epochs

## Troubleshooting

**Model not found error**: Train the model first using `train.py`

**CUDA out of memory**: Reduce batch size or model size in `train.py`

**Service won't start**: Check Python version (3.9+) and dependencies

**No response from AI**: Ensure the model is trained and saved to `data/models/`

## License

MIT License - Part of NyxOS project

