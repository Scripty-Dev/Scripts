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

def setup_vue(path, folder_name):
    full_path = os.path.join(path, folder_name)
    
    print(f"Creating Vue 3 + TypeScript project in: {full_path}")
    
    # Create Vue project with Vite and install initial dependencies
    commands = [
        f"npm create vite@latest {folder_name} -- --template vue-ts --force",
        "npm install",
        "npm install vue-router@4 pinia @vueuse/core",
        "npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.14",
        "npx tailwindcss init -p" 
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd, cwd=path if cmd == commands[0] else full_path):
            return False

    tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}"""

    with open(os.path.join(full_path, 'tailwind.config.js'), 'w') as f:
        f.write(tailwind_config)
        
    # Create PostCSS config
    postcss_config = """export default {
  plugins: {
    'tailwindcss': {},
    autoprefixer: {},
  },
}"""

    with open(os.path.join(full_path, 'postcss.config.js'), 'w') as f:
        f.write(postcss_config)

    # Update App.vue with Scripty branding
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

    with open(os.path.join(full_path, 'src', 'App.vue'), 'w') as f:
        f.write(app_content)

    # Create Home view with fixed template
    home_content = """<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div class="text-center">
    <h1 class="text-4xl font-bold mb-8">
      Vue 3 + TypeScript project initialized by
      <span class="text-emerald-600">Scripty</span>
    </h1>

    <div class="bg-white rounded-xl shadow-lg p-6 mb-8 max-w-2xl mx-auto">
      <p class="text-gray-600 mb-4">
        Edit <code class="bg-gray-100 px-2 py-1 rounded">src/views/HomeView.vue</code> to test HMR
      </p>

      <div class="flex justify-center gap-4 items-center">
        <button
          type="button"
          class="px-4 py-2 font-semibold text-sm bg-emerald-500 text-white rounded-md shadow-sm hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
          @click="count++"
        >
          Count is: {{ count }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
      <!-- First Link -->
      <a
        href="https://vuejs.org/guide/introduction.html"
        target="_blank"
        class="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-emerald-300 hover:bg-emerald-50"
      >
        <h2 class="mb-3 text-2xl font-semibold">
          Documentation
          <span class="inline-block transition-transform group-hover:translate-x-1">-></span>
        </h2>
        <p class="text-sm opacity-70">Find in-depth information about Vue 3 features and API.</p>
      </a>

      <!-- Second Link -->
      <a
        href="https://pinia.vuejs.org/"
        target="_blank"
        class="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-emerald-300 hover:bg-emerald-50"
      >
        <h2 class="mb-3 text-2xl font-semibold">
          Pinia
          <span class="inline-block transition-transform group-hover:translate-x-1">-></span>
        </h2>
        <p class="text-sm opacity-70">Learn about Vue's official state management library.</p>
      </a>
    </div>
  </div>
</template>"""

    os.makedirs(os.path.join(full_path, 'src', 'views'), exist_ok=True)
    with open(os.path.join(full_path, 'src', 'views', 'HomeView.vue'), 'w') as f:
        f.write(home_content)

    # Create About view
    about_content = """<template>
  <div class="text-center">
    <h1 class="text-4xl font-bold mb-8">About</h1>
    <p class="text-lg text-gray-600 max-w-2xl mx-auto">
      This is a Vue 3 project with TypeScript, created using Vite. It includes Vue Router for navigation,
      Pinia for state management, and Tailwind CSS for styling.
    </p>
    <p class="text-2xl font-bold mt-8">Initialized by <span class="text-purple-600">Scripty</span></p>
  </div>
</template>"""

    with open(os.path.join(full_path, 'src', 'views', 'AboutView.vue'), 'w') as f:
        f.write(about_content)

    # Update router
    router_content = """import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    }
  ]
})

export default router"""

    os.makedirs(os.path.join(full_path, 'src', 'router'), exist_ok=True)
    with open(os.path.join(full_path, 'src', 'router', 'index.ts'), 'w') as f:
        f.write(router_content)

    # Create main store with Pinia
    store_content = """import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
  state: () => ({
    count: 0,
    name: 'Vue 3 + TypeScript'
  }),
  getters: {
    doubleCount: (state) => state.count * 2,
  },
  actions: {
    increment() {
      this.count++
    }
  }
})"""

    os.makedirs(os.path.join(full_path, 'src', 'stores'), exist_ok=True)
    with open(os.path.join(full_path, 'src', 'stores', 'main.ts'), 'w') as f:
        f.write(store_content)

    # Update main.ts
    main_content = """import './style.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')"""

    with open(os.path.join(full_path, 'src', 'main.ts'), 'w') as f:
        f.write(main_content)

    # Update style.css
    style_content = """@tailwind base;
@tailwind components;
@tailwind utilities;"""

    with open(os.path.join(full_path, 'src', 'style.css'), 'w') as f:
        f.write(style_content)

    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python vue_setup.py <path> <folder_name>")
        sys.exit(1)
    
    path = sys.argv[1]
    folder_name = sys.argv[2]
    
    if setup_vue(path, folder_name):
        print("Vue 3 + TypeScript setup completed successfully!")
    else:
        print("Setup failed")