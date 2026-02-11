# 🌳 Flowbook

> **Break Free from Linear Notebooks** — A DAG-based notebook environment for non-linear data exploration and research.

Flowbook solves the fundamental limitation of Jupyter notebooks: **linearity**. Traditional notebooks force you down a single path. With Flowbook, explore multiple branches of logic simultaneously, experiment with different transformations, and maintain a clear dependency graph of your entire analysis.

Perfect for data scientists, ML engineers, and analysts who need to explore multiple hypotheses without creating dozens of notebook files.

---

## Screenshot
<img width="970" height="1089" alt="flowbook_screenshot" src="https://github.com/user-attachments/assets/0d6533ec-4eab-4047-bb54-3556c4b6a834" />

## ✨ Key Features

- **🌳 Non-Linear Execution** — Create branching paths of analysis instead of rigid sequential cells
- **🔄 Shared State Management** — Parent nodes automatically pass their state to children; isolation prevents conflicts
- **📊 Visual DAG Editor** — See your analysis structure at a glance with an interactive node-based interface
- **⚡ Real-Time Execution** — Execute nodes individually or follow dependency chains with instant feedback
- **🐳 Containerized** — Single Docker command to run everything; no environment setup needed
- **🐍 Python-Native** — Jupyter kernels under the hood; use any Python library you want

---

## 🎯 The Problem It Solves

### Linear Notebooks Are Limiting

```
Traditional Jupyter:  A → B → C → D → E → F

If you want to test two different approaches starting at C, you usually end up duplicating cells or creating a new notebook.
```

### Flowbook: Explore Multiple Paths

```
           ├─→ C1 (Approach 1) ─→ D1 ─→ E1
A → B ─→ │
           └─→ C2 (Approach 2) ─→ D2 ─→ E2

All paths share state from A and B.
No redundant computation. Easy to compare.
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and navigate to the project
cd Flowbook

# Run everything in one command
docker-compose up --build
```

Open your browser to **http://localhost:8000** 

That's it! The entire frontend + backend is running in a container.

### Option 2: Local Development

**Requirements:**
- Python 3.9+
- Node.js 18+
- npm or yarn

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install and build React frontend
cd flowbook-ui
npm install
npm run build
cd ..

# Start FastAPI backend
uvicorn flowbook.api:app --reload
```

Open your browser to **http://localhost:8000**

---

## 📚 Usage

### Creating a Flowbook

1. Open the editor at http://localhost:8000
2. Click to create nodes (they auto-generate IDs)
3. Write Python code in each node
4. Click "Execute" to run a node (dependencies run automatically)
5. Branch by creating multiple children from one parent

### Example: Data Analysis with Branching

```python
# Node A - Load Data
import pandas as pd
df = pd.read_csv('data.csv')
print(f"Loaded {len(df)} rows")

# Node B - Data Summary (child of A)
print(df.describe())
print(f"Null values: {df.isnull().sum()}")

# Node C1 - Approach 1: Simple Imputation (child of A)
df['age'].fillna(df['age'].median(), inplace=True)

# Node C2 - Approach 2: Drop Nulls (child of A)
df_clean = df.dropna()

# Node D1 - Analyze Approach 1 (child of C1)
print(f"Shape after imputation: {df.shape}")

# Node D2 - Analyze Approach 2 (child of C2)
print(f"Shape after dropping nulls: {df_clean.shape}")
```

Both approaches use the same source data (`A`), but take different paths. You can easily compare results.

---

## 🏗️ Architecture

### Full-Stack Single Container

```
┌─────────────────────────────────────────────────┐
│          Docker Container (Flowbook)            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  React Frontend (Port 8000)              │  │
│  │  - Interactive node editor               │  │
│  │  - DAG visualization                     │  │
│  │  - Real-time output streaming           │  │
│  └──────────────────────────────────────────┘  │
│                      ↕                          │
│  ┌──────────────────────────────────────────┐  │
│  │  FastAPI Backend                         │  │
│  │  - /execute_node endpoint                │  │
│  │  - Dependency resolution                 │  │
│  │  - State serialization                   │  │
│  └──────────────────────────────────────────┘  │
│                      ↕                          │
│  ┌──────────────────────────────────────────┐  │
│  │  Jupyter Kernel (Python)                 │  │
│  │  - Isolated namespace per node           │  │
│  │  - Parent state injection                │  │
│  │  - Output capture & streaming            │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### How Execution Works

1. **User executes Node C** with parent A
2. **Backend resolves dependencies** → finds that C depends on A
3. **Loads parent state** → deserializes A's pickled variables
4. **Injects into namespace** → all of A's variables available in C
5. **Executes C's code** → in an isolated namespace with A's context
6. **Captures output** → streams stdout/stderr/results to UI
7. **Serializes state** → pickles and stores C's new variables
8. **Returns result** → sends to frontend for display

---

## 📁 Project Structure

```
Flowbook/
├── flowbook/                 # Python backend
│   ├── api.py               # FastAPI server + Jupyter kernel management
│   ├── executor.py          # DAG execution logic
│   ├── model.py             # Data models (Node, Flowbook)
│   ├── io.py                # Load/save .fpynb files
│   ├── cli.py               # Command-line interface
│   └── validation.py        # JSON schema validation
├── flowbook-ui/             # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx          # Main editor component
│   │   ├── NodeCell.tsx     # Individual node component
│   │   └── layout.ts        # UI layout utilities
│   └── package.json
├── schema/
│   └── flowbook.schema.json # JSON Schema for .fpynb format
├── examples/
│   └── simple.fpynb         # Example flowbook file
├── Dockerfile               # Single-container build
├── docker-compose.yml       # Orchestration
└── requirements.txt         # Python dependencies
```

---

## 🔧 File Format: `.fpynb`

Flowbook files are `.json`—easy to version control, serialize, and integrate with other tools.

```json
{
  "metadata": {
    "name": "My Analysis",
    "kernel": "python3",
    "format_version": 1
  },
  "root": "A",
  "nodes": {
    "A": {
      "type": "code",
      "source": "x = 10\nprint(x)",
      "parents": [],
      "outputs": []
    },
    "B": {
      "type": "code",
      "source": "y = x + 5\nprint(y)",
      "parents": ["A"],
      "outputs": []
    }
  }
}
```

---

## 💡 Why This Matters for Data Science

### Problem with Jupyter
- ❌ Linear execution only
- ❌ Hard to maintain multiple hypotheses
- ❌ Easy to lose track of what you've tried
- ❌ Difficult to compare alternate approaches

### Flowbook Solution
- ✅ DAG-based execution
- ✅ Multiple branches from single data source
- ✅ Clear dependency visualization
- ✅ Instant hypothesis comparison
- ✅ No duplicate code running
- ✅ Shared state across branches

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19 + TypeScript + ReactFlow (DAG visualization) |
| **Backend** | FastAPI + Uvicorn + Pydantic |
| **Execution** | Jupyter Client + Kernel Manager (isolated Python kernels) |
| **Serialization** | JSON + Pickle (for state snapshots) |
| **Validation** | JSON Schema |
| **Containerization** | Docker + Docker Compose |

---

## 📖 API Reference

### Execute Node

```bash
POST /execute_node
Content-Type: application/json

{
  "nodeId": "C",
  "parentId": "A",
  "code": "y = x * 2\nprint(y)"
}
```

**Response:**
```json
{
  "stdout": "20\n",
  "error": null
}
```

### Health Check

```bash
GET /health
```

Returns `{ "status": "ok" }`

### API Documentation

Interactive docs available at `http://localhost:8000/docs` (Swagger UI)

---

## 🐛 Troubleshooting

### Docker Build Fails
```bash
# Clean Docker cache and rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

### Port 8000 Already in Use
```bash
# Use a different port
docker run -p 8001:8000 flowbook:latest
# Access at http://localhost:8001
```

### Jupyter Kernel Issues
```bash
# Restart the backend
docker-compose restart flowbook
```

