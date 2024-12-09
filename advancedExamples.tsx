import React, { useState, useEffect } from 'react'

// The required object export for ScriptAgent to find and identify the script
export const object = {
    name: 'advancedExample',
    description: 'An example advanced script with UI.',
    parameters: {
        type: 'object',
        properties: {},
        required: []
    }
}

// Export the component as the default export so it can be dynamically imported
export default function AdvancedExample() {
    const [data, setData] = useState<string>('')
    
    // Add any handlers or effects here
    const handleClick = async () => {
        // Handler code
    }
    
    return (
        <div className="p-4">
            <h2 className="text-lg font-bold">Advanced Script</h2>
            <div className="mt-4">
                {/* Your UI content */}
            </div>
        </div>
    )
}
