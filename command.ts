export const func = ({ command }: { command: string }): string => {
    const child_process = require('child_process')
    const output = child_process.execSync(command)
    return `${output.toString()}
Command executed successfully.`
}

export const object = {
    name: 'command',
    description: `Run system commands in the terminal.

IMPORTANT: This script handles file and system operations. When users mention file operations like moving, copying, or unzipping files, use THIS script, not the convert script.

Key triggers to use this script:
- Any mention of files, folders, or directories
- Words like "move", "copy", "unzip", "latest file"
- References to system locations like "downloads folder", "documents", etc.

Check the operating system (provided in your system prompt) and use appropriate commands:

Windows:
"move latest file in downloads to business folder" →
"move %USERPROFILE%\\Downloads\\$(dir /b /od %USERPROFILE%\\Downloads | findstr /v /i \"desktop.ini\" | tail -1) %USERPROFILE%\\Documents\\Business"

Unix/Linux/MacOS:
"move latest file in downloads to business folder" →
"mv $(ls -t ~/Downloads | head -n1) ~/Documents/Business"

Do not attempt to convert these requests to unit conversions or other operations. This is specifically for file and system operations.`,
    parameters: {
        type: 'object',
        properties: {
            command: {
                type: 'string',
                description: 'The system command to execute'
            }
        },
        required: ['command']
    }
}
