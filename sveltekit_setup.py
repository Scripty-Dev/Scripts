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

def setup_sveltekit(path=os.path.expanduser("~"), folder_name="sveltekit-app"):
    full_path = os.path.join(path, folder_name)
    
    print(f"Creating SvelteKit + TypeScript project in: {full_path}")
    
    commands = [
        f"npm create vite@latest {folder_name} -- --template svelte-ts --force",
        "npm install",
        "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14",
        "npx tailwindcss init -p"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=path if cmd == commands[0] else full_path):
            return False

    # Create Tailwind config
    tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
  },
  plugins: [],
}"""

    with open(os.path.join(full_path, 'tailwind.config.js'), 'w') as f:
        f.write(tailwind_config)

    # Update style.css with Tailwind
    css_content = """@tailwind base;
@tailwind components;
@tailwind utilities;"""

    with open(os.path.join(full_path, 'src', 'style.css'), 'w') as f:
        f.write(css_content)

    # Update App.svelte
    app_content = """<script lang="ts">
  import './style.css'
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
  import Counter from './lib/Counter.svelte'
</script>

<main class="min-h-screen flex flex-col items-center justify-center p-8 text-center">
  <div class="flex justify-center gap-8 mb-8">
    <a 
      href="https://vite.dev" 
      target="_blank" 
      rel="noreferrer"
      class="transition-transform hover:scale-110"
    >
      <img 
        src={viteLogo} 
        class="h-24 w-24 p-6 transition-all duration-300 hover:drop-shadow-[0_0_2em_#646cffaa]" 
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
        class="h-24 w-24 p-6 transition-all duration-300 hover:drop-shadow-[0_0_2em_#ff3e00aa]" 
        alt="Svelte Logo" 
      />
    </a>
  </div>

  <h1 class="text-4xl font-bold mb-8">
    Vite + Svelte initialized by 
      <span class="text-purple-500">Scripty</span>
  </h1>

  <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
    <Counter />
  </div>

  <p class="mb-4">
    Check out 
    <a 
      href="https://github.com/sveltejs/kit#readme" 
      target="_blank" 
      rel="noreferrer"
      class="text-blue-600 hover:text-blue-800 underline"
    >
      SvelteKit
    </a>
    , the official Svelte app framework powered by Vite!
  </p>

  <p class="text-gray-500">
    Click on the Vite and Svelte logos to learn more
  </p>
</main>"""

    with open(os.path.join(full_path, 'src', 'App.svelte'), 'w') as f:
        f.write(app_content)

    # Create Counter component
    counter_content = """<script lang="ts">
  let count: number = 0
  const increment = () => {
    count += 1
  }
</script>

<button
  type="button"
  class="px-4 py-2 font-semibold text-sm bg-purple-500 text-white rounded-md shadow-sm hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
  on:click={increment}
>
  count is {count}
</button>"""

    os.makedirs(os.path.join(full_path, 'src', 'lib'), exist_ok=True)
    with open(os.path.join(full_path, 'src', 'lib', 'Counter.svelte'), 'w') as f:
        f.write(counter_content)

    # Create README
    readme_content = f"""# {folder_name}

SvelteKit + TypeScript project initialized by Scripty

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
   ```

## Features
- SvelteKit for full-stack development
- TypeScript for type safety
- Tailwind CSS for styling
- Vite for fast development
"""

    with open(os.path.join(full_path, 'README.md'), 'w') as f:
        f.write(readme_content)

    return True

async def func(args):
    """Handler function for SvelteKit project setup"""
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
            
        if setup_sveltekit(path, folder_name):
            return json.dumps({
                "success": True,
                "message": f"SvelteKit project created successfully in {folder_name}"
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
    "name": "sveltekit_setup",
    "description": "Create a new SvelteKit project with TypeScript and TailwindCSS",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path where the project should be created",
                "default": "~"
            },
            "folder_name": {
                "type": "string",
                "description": "Name of the project folder",
                "default": "sveltekit_project"
            }
        }
    }
}

# Required modules
modules = ['subprocess']