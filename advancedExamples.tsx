import React from 'react'

// The object export for AI integration
export const object = {
    name: 'advancedExample',
    description: 'Example advanced script with UI.',
    parameters: {
        type: 'object',
        properties: {
            message: {
                type: 'string',
                description: 'Message to display'
            }
        },
        required: []
    }
}

// The React component as default export
const AdvancedExample: React.FC = () => {
    return (
        <div className="p-4 bg-gray-800 rounded-lg">
            <h2 className="text-xl font-bold text-white">Advanced Script</h2>
            <div className="mt-4 text-gray-200">
                Example Content
            </div>
        </div>
    )
}

export default AdvancedExample
