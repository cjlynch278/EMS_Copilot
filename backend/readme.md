# EMS Copilot Backend

This is the backend service for the EMS Copilot project, built using FastAPI and following clean architecture principles.

## Project Structure

```
src/ems_copilot/
├── domain/              # Business logic and entities
│   ├── entities/        # Core business objects
│   ├── value_objects/   # Immutable value objects
│   └── services/        # Domain services
├── application/         # Application business rules
│   ├── use_cases/      # Use case implementations
│   └── interfaces/      # Application interfaces
├── infrastructure/      # Frameworks and external services
│   ├── database/       # Database implementations
│   ├── api/            # API implementations
│   └── config/         # Configuration management
└── interfaces/          # Interface adapters
    ├── api/            # API controllers
    └── cli/            # CLI interface
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Sort imports: `isort .`
- Type checking: `mypy .`

## Running the Application

```bash
uvicorn src.ems_copilot.infrastructure.api.main:app --reload
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

SET THIS TO FALSE !!!
You will most likely get a 401 error saying that you need oauth authentication if this is set to true.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
You will need to run gcloud init and gcloud auth application-default login
