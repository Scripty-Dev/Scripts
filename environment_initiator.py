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
        "next-ts": setup_nextjs
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
        sys.exit(1)
    
    path = sys.argv[1]
    folder_name = sys.argv[2]
    template = sys.argv[3]
    
    if setup_environment(path, folder_name, template):
        print("Setup completed successfully!")
    else:
        print("Setup failed")