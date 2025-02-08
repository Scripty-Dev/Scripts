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
        "npm install express cors dotenv mongoose jsonwebtoken bcryptjs --yes",
        "npm install -D typescript @types/node @types/express @types/cors @types/mongoose @types/jsonwebtoken @types/bcryptjs ts-node nodemon --yes",
        "npx tsc --init"  # Removed --yes flag as it's not supported by tsc
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
    
    # Setup Frontend
    print("\nSetting up MERN Frontend...")
    
    frontend_commands = [
        f"npm create vite@latest . --yes -- --template react-ts",
        "npm install --yes",
        "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14 --yes",
        "npm install axios @tanstack/react-query react-router-dom --yes"
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
    
    # Create README
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

async def func(args):
    """Handler function for MERN stack project setup"""
    try:
        # Default to home directory if path not provided or is "."
        path = args.get("path", ".")
        if path == ".":
            path = os.path.expanduser("~")
            
        folder_name = args.get("folder_name")
        
        if not folder_name:
            return json.dumps({
                "success": False,
                "error": "Folder name is required"
            })
            
        if setup_mern(path, folder_name):
            return json.dumps({
                "success": True,
                "message": f"MERN stack project created successfully in {folder_name}"
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
    "name": "mern_setup",
    "description": "Create a new MERN (MongoDB, Express, React, Node.js) stack project with TypeScript and TailwindCSS",
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