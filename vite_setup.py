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

def setup_vite(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    print(f"Creating Vite project in: {full_path}")
    commands = [
        f"npm create vite@latest {folder_name} --yes -- --template react-ts",  # Added --yes flag
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

async def func(args):
    """Handler function for Vite + React project setup"""
    try:
        path = args.get("path", os.path.expanduser("~"))
        folder_name = args.get("folder_name", "vite_project")
        
        if setup_vite(path, folder_name):
            return json.dumps({
                "success": True,
                "message": f"Vite + React project created successfully in {folder_name}"
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
    "name": "vite_setup",
    "description": "Create a new Vite + React project with TypeScript and TailwindCSS",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path where the project should be created",
                "default": os.path.expanduser("~")
            },
            "folder_name": {
                "type": "string",
                "description": "Name of the project folder",
                "default": "vite_project"
            }
        }
    }
}

# Required modules
modules = ['subprocess']