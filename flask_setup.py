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

def modify_css(path):
    css_content = """@tailwind base;
@tailwind components;
@tailwind utilities;"""
    with open(os.path.join(path, 'src', 'index.css'), 'w') as f:
        f.write(css_content)

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

async def func(args):
    """Handler function for Flask + React project setup"""
    try:
        path = args.get("path", ".")
        if path == ".":
            path = os.path.expanduser("~")
            
        folder_name = args.get("folder_name")
        
        if not folder_name:
            return json.dumps({
                "success": False,
                "error": "Folder name is required"
            })
            
        if setup_flask_ts(path, folder_name):
            return json.dumps({
                "success": True,
                "message": f"Flask + React project created successfully in {folder_name}"
            })
        else:
            return json.dumps({
                "success": False,
                "error": "Project setup failed"
            })
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

object = {
    "name": "flask_setup",
    "description": "Create a new Flask + React project with TypeScript and TailwindCSS",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path where the project should be created",
                "default": "."
            },
            "folder_name": {
                "type": "string",
                "description": "Name of the project folder"
            }
        },
        "required": ["folder_name"]
    }
}

# Required modules
modules = ['subprocess']

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python flask_setup.py <path> <folder_name>")
        sys.exit(1)
    
    path = sys.argv[1]
    folder_name = sys.argv[2]
    
    if setup_flask_ts(path, folder_name):
        print("Flask + TypeScript setup completed successfully!")
    else:
        print("Setup failed")