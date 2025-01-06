import { promises as fs } from 'fs'
import path from 'path'
import { execSync } from 'child_process'
import { homedir } from 'os'

export const func = async ({ command, type = 'custom' }: { command: string, type?: 'move' | 'unzip' | 'custom' }): Promise<string> => {
    // Handle common file operations with built-in shortcuts
    if (type === 'move') {
        // Expands ~ to full home directory path
        command = command.replace(/~/g, homedir())
        
        // Handle special keywords
        if (command.includes('latest-download')) {
            const downloadsDir = path.join(homedir(), 'Downloads')
            const files = await fs.readdir(downloadsDir)
            const latest = files
                .map(f => ({ name: f, ctime: fs.stat(path.join(downloadsDir, f)).ctime }))
                .sort((a, b) => b.ctime.getTime() - a.ctime.getTime())[0].name
                
            command = command.replace('latest-download', path.join(downloadsDir, latest))
        }
    }

    if (type === 'unzip') {
        // Add unzip command prefix if not present
        if (!command.startsWith('unzip')) {
            command = `unzip ${command}`
        }
    }

    try {
        const output = execSync(command)
        return `${output.toString()}\nCommand executed successfully.`
    } catch (error) {
        return `Error executing command: ${error.message}`
    }
}

export const object = {
    name: 'command',
    description: `Run file management commands with enhanced functionality.
Examples:
- move latest-download ~/Documents
- unzip archive.zip target_folder
- custom commands`,
    parameters: {
        type: 'object',
        properties: {
            command: {
                type: 'string',
                description: 'The command to execute',
            },
            type: {
                type: 'string',
                enum: ['move', 'unzip', 'custom'],
                description: 'Type of operation to perform',
                default: 'custom'
            }
        },
        required: ['command']
    }
}
