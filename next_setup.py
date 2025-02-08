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

def setup_nextjs(path=os.path.expanduser("~"), folder_name="nextjs-app"):
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

async def func(args):
    """Handler function for Next.js project setup"""
    try:
        path = args.get("path", os.path.expanduser("~"))
        folder_name = args.get("folder_name", "next_project")
        
        if setup_nextjs(path, folder_name):
            return json.dumps({
                "success": True,
                "message": f"Next.js project created successfully in {folder_name}"
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
    "name": "next_setup",
    "description": "Create a new Next.js project with TypeScript and TailwindCSS",
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
                "default": "next_project"
            }
        }
    }
}

# Required modules
modules = ['subprocess']