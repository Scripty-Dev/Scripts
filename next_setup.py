import subprocess
import os
import sys

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

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python next_setup.py <path> <folder_name>")
        sys.exit(1)
    
    path = sys.argv[1]
    folder_name = sys.argv[2]
    
    if setup_nextjs(path, folder_name):
        print("Next.js setup completed successfully!")
    else:
        print("Setup failed")