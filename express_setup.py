import subprocess
import os
import sys
import json
import tkinter as tk
from tkinter import filedialog

def run_command(command, cwd=None):
    try:
        process = subprocess.Popen(
            command, 
            cwd=cwd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Command failed: {stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return False

def setup_express_ts(folder_name="express-ts-app"):
    try:
        # Create and configure root window with HiDPI support
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(2)
        except:
            pass

        root = tk.Tk()
        try:
            root.tk.call('tk', 'scaling', root.winfo_fpixels('1i')/72.0)
        except:
            pass
            
        root.withdraw()
        
        path = filedialog.askdirectory(
            title="Select Directory for Express.js Project"
        )
        
        if not path:
            return False
            
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
    except Exception as e:
        print(f"Error setting up Express.js + TypeScript project: {str(e)}")
        return False

async def func(args):
    """Handler function for Express.js + TypeScript project setup"""
    try:
        path = args.get("path", os.path.expanduser("~"))
        folder_name = args.get("folder_name", "express-ts-app")
        
        if setup_express_ts(folder_name):
            return json.dumps({
                "success": True,
                "message": f"Express.js + TypeScript project created successfully in {folder_name}"
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
    "name": "express_setup",
    "description": "Create a new Express.js + TypeScript project with a predefined structure",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_name": {
                "type": "string",
                "description": "Name of the project folder",
                "default": "express_project"
            }
        }
    }
}

# Required modules
modules = ['subprocess']
