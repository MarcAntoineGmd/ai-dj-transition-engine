# AI DJ Transition Engine

An AI-powered DJ application that analyzes two songs and generates intelligent, beat-aligned transitions.

## Tech Stack

* Frontend: React, TypeScript, Vite
* Backend: Python, FastAPI
* Audio Processing: librosa, NumPy, SciPy
* Machine Learning: PyTorch
* Testing: pytest, Vitest
* Infrastructure: Docker, GitHub Actions

## Project Structure

```text
ai-dj-transition-engine/
├── frontend/
├── backend/
│   ├── app/
│   └── tests/
├── ml/
├── docs/
├── scripts/
├── docker-compose.yml
├── README.md
├── .gitignore
└── LICENSE
```

## Running the Backend

From the `backend` directory:

```bash
cd backend
```

Activate the Python virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI development server:

```bash
python -m uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Running the Frontend

From the `frontend` directory:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

## Development Status

Phase 0 — Project setup and basic frontend/backend communication.
