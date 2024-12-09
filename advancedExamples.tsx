import React, { useState, useEffect } from 'react'

// The object export is used by the AI to understand the script
export const object = {
    name: 'advancedExample',
    description: 'An example advanced script with UI.',
    parameters: {
        type: 'object',
        properties: {
            // Define any parameters the AI can pass to your script
            message: {
                type: 'string',
                description: 'A message to display'
            }
        },
        required: []
    }
}

// The default export is the React component that gets rendered
const AdvancedExample = () => {
    const [data, setData] = useState<string>('')
    
    const handleClick = async () => {
        // Handler code
    }
    
    return (
        <div className="p-4">
            <h2 className="text-lg font-bold">Advanced Script</h2>
            <div className="mt-4">
                <button 
                    onClick={handleClick}
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                >
                    Click Me
                </button>
            </div>
        </div>
    )
}

export default AdvancedExample
