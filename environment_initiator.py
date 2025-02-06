import subprocess
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Common configuration content
TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 20s linear infinite',
      },
    },
  },
  plugins: [],
}"""

POSTCSS_CONFIG = """export default {
  plugins: {
    'tailwindcss/nesting': {},
    tailwindcss: {},
    autoprefixer: {},
  },
}"""

CSS_CONTENT = """@tailwind base;
@tailwind components;
@tailwind utilities;"""

def run_command(command: str, cwd: Optional[str] = None) -> bool:
    """Execute a shell command and return success status"""
    try:
        process = subprocess.Popen(
            command, 
            cwd=cwd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        if stdout: print("Output:", stdout.decode())
        if stderr: print("Errors:", stderr.decode())
            
        return process.returncode == 0
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

class FileManager:
    """Handles file operations for project setup"""
    
    @staticmethod
    def write_file(path: str, content: str) -> None:
        """Write content to a file, creating directories if needed"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def write_json(path: str, content: Dict[str, Any]) -> None:
        """Write JSON content to a file"""
        FileManager.write_file(path, json.dumps(content, indent=2))

class ProjectBuilder:
    """Base class for project setup"""
    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
        self.full_path = os.path.join(path, name)
        
    def create_project(self) -> bool:
        """Template method for project creation"""
        try:
            self._prepare_environment()
            self._install_dependencies()
            self._configure_project()
            return True
        except Exception as e:
            print(f"Error creating project: {e}")
            return False
            
    def _prepare_environment(self) -> None:
        raise NotImplementedError
        
    def _install_dependencies(self) -> None:
        raise NotImplementedError
        
    def _configure_project(self) -> None:
        raise NotImplementedError

    def _setup_tailwind(self) -> None:
        """Common Tailwind setup"""
        FileManager.write_file(
            os.path.join(self.full_path, 'tailwind.config.js'),
            TAILWIND_CONFIG
        )
        FileManager.write_file(
            os.path.join(self.full_path, 'postcss.config.js'),
            POSTCSS_CONFIG
        )
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'index.css'),
            CSS_CONTENT
        )

class ViteReactBuilder(ProjectBuilder):
    """Handles Vite + React project setup"""
    
    def _prepare_environment(self) -> None:
        run_command(f"npm create vite@latest {self.name} -- --template react-ts --force", self.path)
        
    def _install_dependencies(self) -> None:
        commands = [
            "npm install",
            "npm install vue-router@4 pinia @vueuse/core",
            "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14"
        ]
        for cmd in commands:
            run_command(cmd, self.full_path)
            
    def _configure_project(self) -> None:
        self._setup_tailwind()
        
        # Configure Vue app
        app_content = """<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <span class="text-2xl font-bold text-emerald-600">Vue 3</span>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <RouterLink to="/" class="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-emerald-500 text-sm font-medium">
                Home
              </RouterLink>
              <RouterLink to="/about" class="text-gray-500 hover:text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300 text-sm font-medium">
                About
              </RouterLink>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
          <RouterView />
        </div>
      </div>
    </main>
  </div>
</template>"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'App.vue'),
            app_content
        )

class SvelteKitBuilder(ProjectBuilder):
    """Handles SvelteKit project setup"""
    
    def _prepare_environment(self) -> None:
        run_command(f"npm create vite@latest {self.name} -- --template svelte-ts --force", self.path)
        
    def _install_dependencies(self) -> None:
        commands = [
            "npm install",
            "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14"
        ]
        for cmd in commands:
            run_command(cmd, self.full_path)
            
    def _configure_project(self) -> None:
        self._setup_tailwind()
        
        # Configure Svelte app
        app_content = """<script lang="ts">
  import './style.css'
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
</script>

<main class="min-h-screen flex flex-col items-center justify-center p-8 text-center">
  <div class="flex justify-center gap-8 mb-8">
    <a 
      href="https://vitejs.dev" 
      target="_blank" 
      rel="noreferrer"
      class="transition-transform hover:scale-110"
    >
      <img 
        src={viteLogo} 
        class="h-24 w-24 p-6 transition-all duration-300" 
        alt="Vite Logo" 
      />
    </a>
    <a 
      href="https://svelte.dev" 
      target="_blank" 
      rel="noreferrer"
      class="transition-transform hover:scale-110"
    >
      <img 
        src={svelteLogo} 
        class="h-24 w-24 p-6 transition-all duration-300" 
        alt="Svelte Logo" 
      />
    </a>
  </div>

  <h1 class="text-4xl font-bold mb-8">
    Vite + Svelte initialized by 
    <span class="text-purple-500">Scripty</span>
  </h1>

  <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
    <p class="text-gray-600">
      Edit <code class="bg-gray-100 px-2 py-1 rounded">src/App.svelte</code> to get started
    </p>
  </div>
</main>"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'App.svelte'),
            app_content
        )

class ProjectFactory:
    """Factory for creating different types of projects"""
    
    _builders = {
        'vite-react-ts': ViteReactBuilder,
        'next-ts': NextJSBuilder,
        'express-ts': ExpressBuilder,
        'mern': MERNBuilder,
        'flask-ts': FlaskBuilder,
        'fastapi-react': FastAPIBuilder,
        'vue': VueBuilder,
        'sveltekit-ts': SvelteKitBuilder
    }
    
    @classmethod
    def create_project(cls, template: str, path: str, name: str) -> bool:
        builder_class = cls._builders.get(template)
        if not builder_class:
            raise ValueError(f"Unknown template: {template}")
            
        builder = builder_class(path, name)
        return builder.create_project()

async def func(args: Dict[str, Any]) -> str:
    """Main function to handle project initialization"""
    try:
        path = args.get("path", ".")
        folder_name = args.get("folder_name")
        template = args.get("template")
        
        if not folder_name or not template:
            return json.dumps({"error": "Both folder_name and template are required"})
            
        success = ProjectFactory.create_project(template, path, folder_name)
        
        if success:
            return json.dumps({
                "message": f"Successfully created {template} project in {folder_name}",
                "details": {
                    "path": os.path.abspath(os.path.join(path, folder_name)),
                    "template": template,
                    "next_steps": ["cd " + folder_name, "npm install", "npm run dev"]
                }
            })
            
        return json.dumps({"error": "Project setup failed"})
            
    except Exception as e:
        return json.dumps({"error": str(e)})

# Object description for Scripty
object = {
    "name": "environment_initiator",
    "description": "Initialize development environments with modern configurations",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project creation path (defaults to current directory)"
            },
            "folder_name": {
                "type": "string",
                "description": "Project folder name"
            },
            "template": {
                "type": "string",
                "enum": ["vite-react-ts", "next-ts", "express-ts", "mern", 
                        "flask-ts", "fastapi-react", "vue", "sveltekit-ts"],
                "description": "Project template type"
            }
        },
        "required": ["folder_name", "template"]
    }
}
            "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14"
        ]
        for cmd in commands:
            run_command(cmd, self.full_path)
            
    def _configure_project(self) -> None:
        self._setup_tailwind()
        # Add Scripty branding in App.tsx
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
        Vite + React initialized by{' '}
        <span className="text-purple-600">Scripty</span>
      </h1>
      
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <p className="text-gray-600">
          Edit <code className="bg-gray-100 px-2 py-1 rounded">src/App.tsx</code> and save to test HMR
        </p>
      </div>
    </div>
  )
}

export default App"""
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'App.tsx'),
            app_content
        )

class NextJSBuilder(ProjectBuilder):
    """Handles Next.js project setup"""
    
    def _prepare_environment(self) -> None:
        create_command = f"npx create-next-app@latest {self.name} --ts --tailwind --eslint --app --src-dir --import-alias '@/*' -y --no-turbopack --use-npm --yes"
        run_command(create_command, self.path)
        
    def _install_dependencies(self) -> None:
        # Next.js handles dependencies in _prepare_environment
        pass
            
    def _configure_project(self) -> None:
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
        Next.js project initialized by{' '}
        <span className="text-purple-600">Scripty</span>
      </h1>
      
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <p className="text-gray-600">
          Edit <code className="bg-gray-100 px-2 py-1 rounded">src/app/page.tsx</code> to get started
        </p>
      </div>
    </main>
  )
}"""
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'app', 'page.tsx'),
            page_content
        )

class ExpressBuilder(ProjectBuilder):
    """Handles Express.js project setup"""
    
    def _prepare_environment(self) -> None:
        os.makedirs(self.full_path, exist_ok=True)
        
    def _install_dependencies(self) -> None:
        commands = [
            "npm install express cors dotenv",
            "npm install -D typescript @types/node @types/express @types/cors ts-node nodemon",
            "npx tsc --init"
        ]
        for cmd in commands:
            run_command(cmd, self.full_path)
            
    def _configure_project(self) -> None:
        # Create package.json
        package_json = {
            "name": self.name,
            "version": "1.0.0",
            "description": "Express.js + TypeScript API initialized by Scripty",
            "main": "dist/index.js",
            "scripts": {
                "dev": "nodemon",
                "build": "tsc",
                "start": "node dist/index.js"
            }
        }
        FileManager.write_json(
            os.path.join(self.full_path, 'package.json'),
            package_json
        )
        
        # Create source files
        src_content = """import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();
const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/api/hello', (req, res) => {
    res.json({
        message: 'Hello from Express + TypeScript!',
        info: 'This API was initialized by Scripty'
    });
});

app.listen(port, () => {
    console.log(`[server]: Running at http://localhost:${port}`);
});"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'index.ts'),
            src_content
        )

class MERNBuilder(ProjectBuilder):
    """Handles MERN stack project setup"""
    
    def _prepare_environment(self) -> None:
        os.makedirs(os.path.join(self.full_path, 'frontend'), exist_ok=True)
        os.makedirs(os.path.join(self.full_path, 'backend'), exist_ok=True)
        
    def _install_dependencies(self) -> None:
        # Backend dependencies
        backend_commands = [
            "npm install express cors dotenv mongoose",
            "npm install -D typescript @types/node @types/express @types/cors ts-node nodemon"
        ]
        for cmd in backend_commands:
            run_command(cmd, os.path.join(self.full_path, 'backend'))
            
        # Frontend dependencies
        frontend_commands = [
            "npm create vite@latest . -- --template react-ts --force",
            "npm install",
            "npm install axios @tanstack/react-query"
        ]
        for cmd in frontend_commands:
            run_command(cmd, os.path.join(self.full_path, 'frontend'))
            
    def _configure_project(self) -> None:
        # Configure backend
        backend_index = """import express from 'express';
import cors from 'cors';
import mongoose from 'mongoose';

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/health', (_, res) => {
    res.json({ status: 'ok', message: 'MERN Stack API initialized by Scripty' });
});

mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost/mern-app')
    .then(() => {
        app.listen(5000, () => console.log('Server running on port 5000'));
    });"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'backend', 'src', 'index.ts'),
            backend_index
        )
        
        # Configure frontend
        self._setup_tailwind()

class FlaskBuilder(ProjectBuilder):
    """Handles Flask project setup"""
    
    def _prepare_environment(self) -> None:
        os.makedirs(os.path.join(self.full_path, 'backend'), exist_ok=True)
        os.makedirs(os.path.join(self.full_path, 'frontend'), exist_ok=True)
        
    def _install_dependencies(self) -> None:
        # Setup frontend
        frontend_commands = [
            "npm create vite@latest . -- --template react-ts --force",
            "npm install",
            "npm install -D tailwindcss postcss autoprefixer"
        ]
        for cmd in frontend_commands:
            run_command(cmd, os.path.join(self.full_path, 'frontend'))
            
    def _configure_project(self) -> None:
        # Create Flask backend
        app_content = """from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/hello')
def hello():
    return {'message': 'Flask backend initialized by Scripty'}

if __name__ == '__main__':
    app.run(debug=True)"""
            
        FileManager.write_file(
            os.path.join(self.full_path, 'backend', 'app.py'),
            app_content
        )
        
        # Configure frontend
        self._setup_tailwind()

class FastAPIBuilder(ProjectBuilder):
    """Handles FastAPI project setup"""
    
    def _prepare_environment(self) -> None:
        os.makedirs(os.path.join(self.full_path, 'backend'), exist_ok=True)
        os.makedirs(os.path.join(self.full_path, 'frontend'), exist_ok=True)
        
    def _install_dependencies(self) -> None:
        # Setup frontend
        frontend_commands = [
            "npm create vite@latest . -- --template react-ts --force",
            "npm install",
            "npm install -D tailwindcss postcss autoprefixer",
            "npm install @tanstack/react-query axios"
        ]
        for cmd in frontend_commands:
            run_command(cmd, os.path.join(self.full_path, 'frontend'))
            
    def _configure_project(self) -> None:
        # Create FastAPI backend
        main_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
async def hello():
    return {"message": "FastAPI backend initialized by Scripty"}"""
            
        FileManager.write_file(
            os.path.join(self.full_path, 'backend', 'main.py'),
            main_content
        )
        
        # Configure frontend
        self._setup_tailwind()

class VueBuilder(ProjectBuilder):
    """Handles Vue.js project setup"""
    
    def _prepare_environment(self) -> None:
        run_command(f"npm create vite@latest {self.name} -- --template vue-ts --force", self.path)
        
    def _install_dependencies(self) -> None:
        commands = [
            "npm install",
            "npm install vue-router@4 pinia @vueuse/core",
            "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14"
        ]
        for cmd in commands:
            run_command(cmd, self.full_path)
            
    def _configure_project(self) -> None:
        self._setup_tailwind()
        
        # Configure Vue app
        app_content = """<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <span class="text-2xl font-bold text-emerald-600">Vue 3</span>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <RouterLink to="/" class="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-emerald-500 text-sm font-medium">
                Home
              </RouterLink>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
          <h1 class="text-4xl font-bold mb-8">
            Vue 3 + TypeScript initialized by{' '}
            <span class="text-purple-600">Scripty</span>
          </h1>
          <RouterView />
        </div>
      </div>
    </main>
  </div>
</template>"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'App.vue'),
            app_content
        )
        
        # Create router configuration
        router_content = """import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    }
  ]
})

export default router"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'router', 'index.ts'),
            router_content
        )
        
        # Create home view
        home_content = """<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div class="text-center">
    <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
      <p class="text-gray-600 mb-4">
        Edit <code class="bg-gray-100 px-2 py-1 rounded">src/views/HomeView.vue</code> to test HMR
      </p>

      <button
        type="button"
        class="px-4 py-2 font-semibold text-sm bg-emerald-500 text-white rounded-md shadow-sm hover:bg-emerald-600"
        @click="count++"
      >
        Count is: {{ count }}
      </button>
    </div>
  </div>
</template>"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'views', 'HomeView.vue'),
            home_content
        )

class SvelteKitBuilder(ProjectBuilder):
    """Handles SvelteKit project setup"""
    
    def _prepare_environment(self) -> None:
        run_command(f"npm create vite@latest {self.name} -- --template svelte-ts --force", self.path)
        
    def _install_dependencies(self) -> None:
        commands = [
            "npm install",
            "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14"
        ]
        for cmd in commands:
            run_command(cmd, self.full_path)
            
    def _configure_project(self) -> None:
        self._setup_tailwind()
        
        # Configure Svelte app
        app_content = """<script lang="ts">
  import './style.css'
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
</script>

<main class="min-h-screen flex flex-col items-center justify-center p-8 text-center">
  <div class="flex justify-center gap-8 mb-8">
    <a 
      href="https://vitejs.dev" 
      target="_blank" 
      rel="noreferrer"
      class="transition-transform hover:scale-110"
    >
      <img 
        src={viteLogo} 
        class="h-24 w-24 p-6 transition-all duration-300" 
        alt="Vite Logo" 
      />
    </a>
    <a 
      href="https://svelte.dev" 
      target="_blank" 
      rel="noreferrer"
      class="transition-transform hover:scale-110"
    >
      <img 
        src={svelteLogo} 
        class="h-24 w-24 p-6 transition-all duration-300" 
        alt="Svelte Logo" 
      />
    </a>
  </div>

  <h1 class="text-4xl font-bold mb-8">
    Vite + Svelte initialized by 
    <span class="text-purple-500">Scripty</span>
  </h1>

  <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
    <p class="text-gray-600">
      Edit <code class="bg-gray-100 px-2 py-1 rounded">src/App.svelte</code> to get started
    </p>
  </div>
</main>"""
        
        FileManager.write_file(
            os.path.join(self.full_path, 'src', 'App.svelte'),
            app_content
        )

class ProjectFactory:
    """Factory for creating different types of projects"""
    
    _builders = {
        'vite-react-ts': ViteReactBuilder,
        'next-ts': NextJSBuilder,
        'express-ts': ExpressBuilder,
        'mern': MERNBuilder,
        'flask-ts': FlaskBuilder,
        'fastapi-react': FastAPIBuilder,
        'vue': VueBuilder,
        'sveltekit-ts': SvelteKitBuilder
    }
    
    @classmethod
    def create_project(cls, template: str, path: str, name: str) -> bool:
        builder_class = cls._builders.get(template)
        if not builder_class:
            raise ValueError(f"Unknown template: {template}")
            
        builder = builder_class(path, name)
        return builder.create_project()

async def func(args: Dict[str, Any]) -> str:
    """Main function to handle project initialization"""
    try:
        path = args.get("path", ".")
        folder_name = args.get("folder_name")
        template = args.get("template")
        
        if not folder_name or not template:
            return json.dumps({"error": "Both folder_name and template are required"})
            
        success = ProjectFactory.create_project(template, path, folder_name)
        
        if success:
            return json.dumps({
                "message": f"Successfully created {template} project in {folder_name}",
                "details": {
                    "path": os.path.abspath(os.path.join(path, folder_name)),
                    "template": template,
                    "next_steps": ["cd " + folder_name, "npm install", "npm run dev"]
                }
            })
            
        return json.dumps({"error": "Project setup failed"})
            
    except Exception as e:
        return json.dumps({"error": str(e)})

# Object description for Scripty
object = {
    "name": "environment_initiator",
    "description": "Initialize development environments with modern configurations",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project creation path (defaults to current directory)"
            },
            "folder_name": {
                "type": "string",
                "description": "Project folder name"
            },
            "template": {
                "type": "string",
                "enum": ["vite-react-ts", "next-ts", "express-ts", "mern", 
                        "flask-ts", "fastapi-react", "vue", "sveltekit-ts"],
                "description": "Project template type"
            }
        },
        "required": ["folder_name", "template"]
    }
}
