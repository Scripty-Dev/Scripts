import subprocess
import os
import sys
import json

def run_command(command, cwd=None):
    try:
        print(f"Executing command: {command}")
        process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if stdout:
            print("Output:", stdout.decode())
        if stderr:
            print("Errors:", stderr.decode())
            
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

def modify_css(path):
    css_content = """@tailwind base;
@tailwind components;
@tailwind utilities;"""
    with open(os.path.join(path, 'src', 'index.css'), 'w') as f:
        f.write(css_content)

def create_tailwind_config(path):
    config_content = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 20s linear infinite',
      },
    },
  },
  plugins: [],
}"""
    with open(os.path.join(path, 'tailwind.config.js'), 'w') as f:
        f.write(config_content)

def create_postcss_config(path):
    config_content = """export default {
  plugins: {
    'tailwindcss/nesting': {},
    tailwindcss: {},
    autoprefixer: {},
  },
}"""
    with open(os.path.join(path, 'postcss.config.js'), 'w') as f:
        f.write(config_content)

def update_app_tsx(path):
    app_content = """import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="flex gap-8 mb-8">
        <a href="https://vite.dev" target="_blank" className="hover:scale-110 transition-transform">
          <img src={viteLogo} className="h-32 w-32" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" className="hover:scale-110 transition-transform">
          <img src={reactLogo} className="h-32 w-32 animate-spin-slow" alt="React logo" />
        </a>
      </div>
      
      <h1 className="text-4xl font-bold mb-8">
        Vite + React + Tailwind project initialized by{' '}
        <span className="text-purple-600">Scripty</span>
      </h1>
      
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <p className="text-gray-600">
          Edit <code className="bg-gray-100 px-2 py-1 rounded">src/App.tsx</code> and save to test HMR
        </p>
      </div>

      <p className="text-gray-500">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  )
}

export default App"""
    with open(os.path.join(path, 'src', 'App.tsx'), 'w') as f:
        f.write(app_content)

def setup_nextjs(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    print(f"Creating Next.js project in: {full_path}")
    
    # Create Next.js project with TypeScript and Tailwind
    create_command = f"npx create-next-app@latest {folder_name} --ts --tailwind --eslint --app --src-dir --import-alias '@/*' -y --no-turbopack --use-npm --yes"
    
    if not run_command(create_command, cwd=path):
        return False
        
    # Update the page.tsx with custom content
    page_content = """import Image from 'next/image'

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="flex gap-8 mb-8">
        <div className="hover:scale-110 transition-transform">
          <Image
            src="/next.svg"
            alt="Next.js Logo"
            width={180}
            height={37}
            priority
          />
        </div>
      </div>
      
      <h1 className="text-4xl font-bold mb-8">
        Next.js + TypeScript + Tailwind project initialized by{' '}
        <span className="text-purple-600">Scripty</span>
      </h1>
      
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <p className="text-gray-600">
          Edit <code className="bg-gray-100 px-2 py-1 rounded">src/app/page.tsx</code> and save to test HMR
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <a
          href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template&utm_campaign=create-next-app"
          className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
          target="_blank"
          rel="noopener noreferrer"
        >
          <h2 className="mb-3 text-2xl font-semibold">
            Docs{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Find in-depth information about Next.js features and API.
          </p>
        </a>
      </div>
    </main>
  )
}"""
    
    with open(os.path.join(full_path, 'src', 'app', 'page.tsx'), 'w') as f:
        f.write(page_content)
        
    return True

def setup_express_ts(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    print(f"Creating Express.js + TypeScript project in: {full_path}")
    
    # Create project directory
    os.makedirs(full_path, exist_ok=True)
    
    # Initialize package.json
    package_json = {
        "name": folder_name,
        "version": "1.0.0",
        "description": "Express.js + TypeScript API initialized by Scripty",
        "main": "dist/index.js",
        "scripts": {
            "dev": "nodemon",
            "build": "tsc",
            "start": "node dist/index.js",
            "watch": "tsc -w"
        }
    }
    
    with open(os.path.join(full_path, 'package.json'), 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Install dependencies
    commands = [
        "npm install express cors dotenv",
        "npm install -D typescript @types/node @types/express @types/cors ts-node nodemon",
        "npx tsc --init"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=full_path):
            return False
    
    # Create tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "es2017",
            "module": "commonjs",
            "outDir": "./dist",
            "rootDir": "./src",
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "forceConsistentCasingInFileNames": True
        },
        "include": ["src/**/*"],
        "exclude": ["node_modules"]
    }
    
    with open(os.path.join(full_path, 'tsconfig.json'), 'w') as f:
        json.dump(tsconfig, f, indent=2)
    
    # Create nodemon.json
    nodemon_config = {
        "watch": ["src"],
        "ext": ".ts,.js",
        "ignore": [],
        "exec": "ts-node ./src/index.ts"
    }
    
    with open(os.path.join(full_path, 'nodemon.json'), 'w') as f:
        json.dump(nodemon_config, f, indent=2)
    
    # Create .env
    env_content = """PORT=3000
NODE_ENV=development"""
    
    with open(os.path.join(full_path, '.env'), 'w') as f:
        f.write(env_content)
    
    # Create source directory structure
    src_dir = os.path.join(full_path, 'src')
    routes_dir = os.path.join(src_dir, 'routes')
    middleware_dir = os.path.join(src_dir, 'middleware')
    
    os.makedirs(src_dir)
    os.makedirs(routes_dir)
    os.makedirs(middleware_dir)
    
    # Create main server file
    server_content = """import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { errorHandler } from './middleware/errorHandler';
import indexRouter from './routes';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/', indexRouter);

// Error handling
app.use(errorHandler);

app.listen(port, () => {
    console.log(`[server]: Server is running at http://localhost:${port}`);
    console.log(`Environment: ${process.env.NODE_ENV}`);
});"""
    
    with open(os.path.join(src_dir, 'index.ts'), 'w') as f:
        f.write(server_content)
    
    # Create error handler middleware
    error_handler_content = """import { Request, Response, NextFunction } from 'express';

export const errorHandler = (
    err: Error,
    req: Request,
    res: Response,
    next: NextFunction
) => {
    console.error(err.stack);
    res.status(500).json({
        status: 'error',
        message: 'Internal Server Error'
    });
};"""
    
    with open(os.path.join(middleware_dir, 'errorHandler.ts'), 'w') as f:
        f.write(error_handler_content)
    
    # Create index router
    router_content = """import express from 'express';
const router = express.Router();

// Health check endpoint
router.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        message: 'Server is healthy',
        timestamp: new Date().toISOString()
    });
});

// Example endpoint
router.get('/api/hello', (req, res) => {
    res.json({
        message: 'Hello from Express + TypeScript!',
        info: 'This API was initialized by Scripty'
    });
});

export default router;"""
    
    with open(os.path.join(routes_dir, 'index.ts'), 'w') as f:
        f.write(router_content)
    
    # Create README
    readme_content = f"""# {folder_name}

Express.js + TypeScript API initialized by Scripty

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   npm start
   ```

## Available Scripts

- `npm run dev`: Start development server with hot-reload
- `npm run build`: Build for production
- `npm start`: Start production server
- `npm run watch`: Watch for changes and rebuild

## API Endpoints

- `GET /health`: Health check endpoint
- `GET /api/hello`: Example endpoint

## Environment Variables

- `PORT`: Server port (default: 3000)
- `NODE_ENV`: Environment name (development/production)
"""
    
    with open(os.path.join(full_path, 'README.md'), 'w') as f:
        f.write(readme_content)
        
    return True

def setup_mern(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    # Create main project directories
    backend_path = os.path.join(full_path, 'backend')
    frontend_path = os.path.join(full_path, 'frontend')
    
    os.makedirs(full_path)
    os.makedirs(backend_path)
    os.makedirs(frontend_path)
    
    # Setup Backend
    print("\nSetting up MERN Backend...")
    
    # Initialize backend package.json with corrected scripts
    backend_package = {
        "name": f"{folder_name}-backend",
        "version": "1.0.0",
        "description": "MERN Stack Backend initialized by Scripty",
        "main": "src/index.ts",
        "scripts": {
            "dev": "nodemon src/index.ts",
            "build": "tsc",
            "start": "node dist/index.js"
        }
    }
    
    with open(os.path.join(backend_path, 'package.json'), 'w') as f:
        json.dump(backend_package, f, indent=2)
    
    # Install backend dependencies
    backend_commands = [
        "npm install express cors dotenv mongoose jsonwebtoken bcryptjs",
        "npm install -D typescript @types/node @types/express @types/cors @types/mongoose @types/jsonwebtoken @types/bcryptjs ts-node nodemon",
        "npx tsc --init"
    ]
    
    for cmd in backend_commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=backend_path):
            return False

    # Create backend directory structure
    backend_src = os.path.join(backend_path, 'src')
    os.makedirs(os.path.join(backend_src, 'routes'), exist_ok=True)
    os.makedirs(os.path.join(backend_src, 'models'), exist_ok=True)
    os.makedirs(os.path.join(backend_src, 'middleware'), exist_ok=True)
    
    # Create nodemon.json
    nodemon_config = {
        "watch": ["src"],
        "ext": ".ts,.js",
        "ignore": [],
        "exec": "ts-node ./src/index.ts"
    }
    
    with open(os.path.join(backend_path, 'nodemon.json'), 'w') as f:
        json.dump(nodemon_config, f, indent=2)
    
    # Create main server file (index.ts)
    server_content = """import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Basic route for testing
app.get('/api/test', (req, res) => {
  res.json({ message: 'Backend is working! Initialize by Scripty' });
});

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
  console.log(`Environment: ${process.env.NODE_ENV}`);
});"""

    with open(os.path.join(backend_src, 'index.ts'), 'w') as f:
        f.write(server_content)
    
    # Create backend .env
    env_content = """PORT=5000
MONGODB_URI=mongodb://localhost:27017/mern_db
JWT_SECRET=your_jwt_secret
NODE_ENV=development"""
    
    with open(os.path.join(backend_path, '.env'), 'w') as f:
        f.write(env_content)

    # Create tsconfig.json with correct settings
    tsconfig = {
        "compilerOptions": {
            "target": "es2017",
            "module": "commonjs",
            "outDir": "./dist",
            "rootDir": "./src",
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "forceConsistentCasingInFileNames": True
        },
        "include": ["src/**/*"],
        "exclude": ["node_modules"]
    }
    
    with open(os.path.join(backend_path, 'tsconfig.json'), 'w') as f:
        json.dump(tsconfig, f, indent=2)
    
    # [Rest of the frontend setup remains the same]
    # Setup Frontend
    print("\nSetting up MERN Frontend...")
    
    frontend_commands = [
        f"npm create vite@latest . -- --template react-ts --force",
        "npm install",
        "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14",
        "npm install axios @tanstack/react-query react-router-dom"
    ]
    
    for cmd in frontend_commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=frontend_path):
            return False
    
    # Use the same helper functions as setup_vite
    create_tailwind_config(frontend_path)
    create_postcss_config(frontend_path)
    modify_css(frontend_path)
    
    # Create frontend .env
    frontend_env = """VITE_API_URL=http://localhost:5000/api"""
    
    with open(os.path.join(frontend_path, '.env'), 'w') as f:
        f.write(frontend_env)
    
    # Update App.tsx with MERN-specific content
    app_content = """import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow">
            <div className="max-w-7xl mx-auto py-6 px-4">
              <h1 className="text-3xl font-bold text-gray-900">
                MERN Stack App <span className="text-purple-600">by Scripty</span>
              </h1>
            </div>
          </header>
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              <Routes>
                <Route path="/" element={<div>Welcome to your MERN Stack app!</div>} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App"""
    
    with open(os.path.join(frontend_path, 'src', 'App.tsx'), 'w') as f:
        f.write(app_content)
    
    # Create README without code blocks
    readme_content = f"""# {folder_name}

MERN (MongoDB, Express, React, Node.js) Stack project initialized by Scripty

## Project Structure
{folder_name}/
- backend/         # Express + TypeScript backend
- frontend/        # React + TypeScript frontend

## Getting Started

1. Start MongoDB locally or update MONGODB_URI in backend/.env

2. Start the backend:
   cd backend
   npm install
   npm run dev

3. Start the frontend:
   cd frontend
   npm install
   npm run dev"""
    
    with open(os.path.join(full_path, 'README.md'), 'w') as f:
        f.write(readme_content)
        
    return True

def setup_flask_ts(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    # Create main project directories
    backend_path = os.path.join(full_path, 'backend')
    frontend_path = os.path.join(full_path, 'frontend')
    
    os.makedirs(full_path)
    os.makedirs(backend_path)
    os.makedirs(frontend_path)
    
    # Setup Backend
    print("\nSetting up Flask Backend...")
    
    # Create backend structure
    backend_app = os.path.join(backend_path, 'app')
    os.makedirs(os.path.join(backend_app, 'routes'), exist_ok=True)
    os.makedirs(os.path.join(backend_app, 'models'), exist_ok=True)
    os.makedirs(os.path.join(backend_app, 'schemas'), exist_ok=True)
    
    # Create pyproject.toml for Poetry
    pyproject_content = """[tool.poetry]
name = "flask-ts-backend"
version = "0.1.0"
description = "Flask backend initialized by Scripty"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
flask = "^3.0.0"
flask-cors = "^4.0.0"
python-dotenv = "^1.0.0"
flask-sqlalchemy = "^3.1.0"
marshmallow = "^3.20.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.7.0"
mypy = "^1.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"""

    with open(os.path.join(backend_path, 'pyproject.toml'), 'w') as f:
        f.write(pyproject_content)
    
    # Create main app file
    app_content = """from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Register routes
    from app.routes import main
    app.register_blueprint(main.bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000)"""
    
    with open(os.path.join(backend_app, '__init__.py'), 'w') as f:
        f.write(app_content)
    
    # Create routes
    routes_content = """from flask import Blueprint, jsonify

bp = Blueprint('main', __name__, url_prefix='/api')

@bp.route('/test')
def test():
    return jsonify({'message': 'Flask backend is working! Initialized by Scripty'})"""
    
    with open(os.path.join(backend_app, 'routes', 'main.py'), 'w') as f:
        f.write(routes_content)
    
    # Create models
    models_content = """from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Example model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'"""
    
    with open(os.path.join(backend_app, 'models', '__init__.py'), 'w') as f:
        f.write(models_content)
    
    # Create .env
    env_content = """FLASK_APP=app
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-here"""
    
    with open(os.path.join(backend_path, '.env'), 'w') as f:
        f.write(env_content)
    
    # Create requirements.txt as backup
    requirements_content = """flask>=3.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
flask-sqlalchemy>=3.1.0
marshmallow>=3.20.0"""
    
    with open(os.path.join(backend_path, 'requirements.txt'), 'w') as f:
        f.write(requirements_content)
    
    # Setup Frontend (reuse Vite setup)
    print("\nSetting up TypeScript Frontend...")
    
    frontend_commands = [
        f"npm create vite@latest . -- --template react-ts --force",
        "npm install",
        "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14",
        "npm install axios @tanstack/react-query react-router-dom"
    ]
    
    for cmd in frontend_commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=frontend_path):
            return False
    
    # Use the same helper functions as setup_vite
    create_tailwind_config(frontend_path)
    create_postcss_config(frontend_path)
    modify_css(frontend_path)
    
    # Create frontend .env
    frontend_env = """VITE_API_URL=http://localhost:5000/api"""
    
    with open(os.path.join(frontend_path, '.env'), 'w') as f:
        f.write(frontend_env)
    
    # Create App.tsx with Flask backend test
    app_content = """import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import axios from 'axios'

const queryClient = new QueryClient()

function App() {
  const [backendMessage, setBackendMessage] = useState('')

  useEffect(() => {
    axios.get('http://localhost:5000/api/test')
      .then(response => setBackendMessage(response.data.message))
      .catch(error => console.error('Error:', error))
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow">
            <div className="max-w-7xl mx-auto py-6 px-4">
              <h1 className="text-3xl font-bold text-gray-900">
                Flask + TypeScript App <span className="text-purple-600">by Scripty</span>
              </h1>
            </div>
          </header>
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <p className="text-gray-600">Backend Message:</p>
                <p className="text-lg font-semibold mt-2">{backendMessage}</p>
              </div>
              <Routes>
                <Route path="/" element={<div>Welcome to your Flask + TypeScript app!</div>} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App"""
    
    with open(os.path.join(frontend_path, 'src', 'App.tsx'), 'w') as f:
        f.write(app_content)
    
    # Create README
    readme_content = f"""# {folder_name}

Flask + TypeScript Stack project initialized by Scripty

## Project Structure
{folder_name}/
- backend/         # Flask Python backend
- frontend/        # React TypeScript frontend

## Getting Started

1. Start the backend:
   cd backend
   # If using Poetry:
   poetry install
   poetry run flask run
   # If using pip:
   pip install -r requirements.txt
   flask run

2. Start the frontend:
   cd frontend
   npm install
   npm run dev"""
    
    with open(os.path.join(full_path, 'README.md'), 'w') as f:
        f.write(readme_content)
        
    return True

def setup_fastapi_react(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    # Create main project directories
    backend_path = os.path.join(full_path, 'backend')
    frontend_path = os.path.join(full_path, 'frontend')
    
    os.makedirs(full_path)
    os.makedirs(backend_path)
    os.makedirs(frontend_path)
    
    # Backend setup
    print("\nSetting up FastAPI Backend...")
    
    # Create backend structure
    backend_app = os.path.join(backend_path, 'app')
    os.makedirs(os.path.join(backend_app, 'routers'), exist_ok=True)
    os.makedirs(os.path.join(backend_app, 'models'), exist_ok=True)
    os.makedirs(os.path.join(backend_app, 'schemas'), exist_ok=True)
    
    # Create pyproject.toml for Poetry
    pyproject_content = """[tool.poetry]
name = "fastapi-react-backend"
version = "0.1.0"
description = "FastAPI backend initialized by Scripty"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.109.0"
uvicorn = "^0.27.0"
pydantic = "^2.6.0"
sqlalchemy = "^2.0.25"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.7.0"
mypy = "^1.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"""

    with open(os.path.join(backend_path, 'pyproject.toml'), 'w') as f:
        f.write(pyproject_content)

    # Create main.py
    main_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="FastAPI Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/test")
async def test():
    return {"message": "FastAPI backend is working! Initialized by Scripty"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
"""

    with open(os.path.join(backend_path, 'main.py'), 'w') as f:
        f.write(main_content)

    # Create .env
    env_content = """PORT=8000
DATABASE_URL=sqlite:///./app.db
ENVIRONMENT=development"""

    with open(os.path.join(backend_path, '.env'), 'w') as f:
        f.write(env_content)

    # Create requirements.txt as backup
    requirements_content = """fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.6.0
sqlalchemy>=2.0.25
python-dotenv>=1.0.0"""

    with open(os.path.join(backend_path, 'requirements.txt'), 'w') as f:
        f.write(requirements_content)

    # Frontend setup (reuse our Vite setup)
    print("\nSetting up React Frontend...")
    
    frontend_commands = [
        f"npm create vite@latest . -- --template react-ts --force",
        "npm install",
        "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14",
        "npm install axios @tanstack/react-query react-router-dom"
    ]
    
    for cmd in frontend_commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=frontend_path):
            return False

    # Use helper functions
    create_tailwind_config(frontend_path)
    create_postcss_config(frontend_path)
    modify_css(frontend_path)

    # Create frontend .env
    frontend_env = """VITE_API_URL=http://localhost:8000/api"""
    
    with open(os.path.join(frontend_path, '.env'), 'w') as f:
        f.write(frontend_env)

    # Create App.tsx with FastAPI test
    app_content = """import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import axios from 'axios'

const queryClient = new QueryClient()

function App() {
  const [backendMessage, setBackendMessage] = useState('')

  useEffect(() => {
    axios.get('http://localhost:8000/api/test')
      .then(response => setBackendMessage(response.data.message))
      .catch(error => console.error('Error:', error))
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow">
            <div className="max-w-7xl mx-auto py-6 px-4">
              <h1 className="text-3xl font-bold text-gray-900">
                FastAPI + React App <span className="text-purple-600">by Scripty</span>
              </h1>
            </div>
          </header>
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <p className="text-gray-600">Backend Message:</p>
                <p className="text-lg font-semibold mt-2">{backendMessage}</p>
              </div>
              <div className="mt-8">
                <a 
                  href="http://localhost:8000/docs" 
                  target="_blank"
                  className="text-blue-600 hover:text-blue-800"
                >
                  View FastAPI Documentation -&gt;
                </a>
              </div>
              <Routes>
                <Route path="/" element={<div className="mt-8">Welcome to your FastAPI + React app!</div>} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App"""
    
    with open(os.path.join(frontend_path, 'src', 'App.tsx'), 'w') as f:
        f.write(app_content)

    # Create README
    readme_content = f"""# {folder_name}

FastAPI + React Stack project initialized by Scripty

## Project Structure
{folder_name}/
- backend/         # FastAPI Python backend
- frontend/        # React TypeScript frontend

## Getting Started

1. Start the backend:
   cd backend
   # If using Poetry:
   poetry install
   poetry run uvicorn main:app --reload
   # If using pip:
   pip install -r requirements.txt
   uvicorn main:app --reload

2. Start the frontend:
   cd frontend
   npm install
   npm run dev

## Features
- Interactive API docs at http://localhost:8000/docs
- React Query for data fetching
- TailwindCSS for styling
- TypeScript for type safety"""

    with open(os.path.join(full_path, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
        
    return True

def setup_vite(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    print(f"Creating Vite project in: {full_path}")
    commands = [
        f"npm create vite@latest {folder_name} -- --template react-ts --force",
        "npm install",
        "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=path if cmd == commands[0] else full_path):
            return False

    create_tailwind_config(full_path)
    create_postcss_config(full_path)
    modify_css(full_path)
    update_app_tsx(full_path)
    return True

def setup_environment(path, folder_name, template):
    setup_functions = {
        "vite-react-ts": setup_vite,
        "next-ts": setup_nextjs,
        "express-ts": setup_express_ts,
        "mern": setup_mern,
        "flask-ts": setup_flask_ts,
        "fastapi-react": setup_fastapi_react
    }
    
    if template not in setup_functions:
        print(f"Unknown template: {template}")
        return False
        
    return setup_functions[template](path, folder_name)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <path> <folder_name> <template>")
        print("Available templates:")
        print("  - vite-react-ts")
        print("  - next-ts")
        print("  - express-ts")
        print("  - mern")
        print("  - flask-ts")
        print("  - fastapi-react")

        sys.exit(1)
    
    path = sys.argv[1]
    folder_name = sys.argv[2]
    template = sys.argv[3]
    
    if setup_environment(path, folder_name, template):
        print("Setup completed successfully!")
    else:
        print("Setup failed")