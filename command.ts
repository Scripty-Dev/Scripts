export const func = ({ command }: { command: string }): string => {
    const child_process = require('child_process')
    const output = child_process.execSync(command)
    return `${output.toString()}
Command executed successfully.`
}

export const object = {
    name: 'command',
    description: `Run a command in the terminal.

IMPORTANT: Convert natural language into the appropriate command for the user's operating system.

Windows Examples:
"move latest file in downloads to business folder" →
"move %USERPROFILE%\\Downloads\\$(dir /b /od %USERPROFILE%\\Downloads | findstr /v /i \"desktop.ini\" | tail -1) %USERPROFILE%\\Documents\\Business"

"unzip photos.zip to Pictures" →
"tar -xf %USERPROFILE%\\photos.zip -C %USERPROFILE%\\Pictures"

Unix/Linux/MacOS Examples:
"move latest file in downloads to business folder" →
"mv $(ls -t ~/Downloads | head -n1) ~/Documents/Business"

"unzip photos.zip to Pictures" →
"unzip ~/photos.zip -d ~/Pictures"

Check the operating system before converting commands. Use:
- Windows: %USERPROFILE%, move, copy, dir
- Unix/Linux/MacOS: ~/, mv, cp, ls

Do not tell them to manually do the task. Do not explain the command translation.`,
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
