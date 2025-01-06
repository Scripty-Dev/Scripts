export const func = ({ command }: { command: string }): string => {
    const child_process = require('child_process')
    const output = child_process.execSync(command)
    return `${output.toString()}
Command executed successfully.`
}

export const object = {
    name: 'command',
    description: `Run a command in the terminal.

IMPORTANT: You must convert natural language requests into proper system commands before execution.

Examples:
Input: "move the latest file in my downloads folder to my business folder"
You should convert to: "mv $(ls -t ~/Downloads | head -n1) ~/Documents/Business"

Input: "unzip my photos.zip into Pictures"
You should convert to: "unzip ~/photos.zip -d ~/Pictures"

Always:
- Convert user paths like "downloads folder" to proper system paths (~/Downloads)
- For latest file commands, use "ls -t | head -n1" pattern
- Use proper system commands (mv, cp, unzip, etc.)
- Include full paths with ~ for home directory
- Handle spaces in filenames properly with quotes

Do not tell them to manually do the task. Do not explain the command translation to the user.`,
    parameters: {
        type: 'object',
        properties: {
            command: {
                type: 'string',
                description: 'The command to run in the terminal'
            }
        },
        required: ['command']
    }
}
