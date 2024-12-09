const React = require('react')

// The object export for the AI
exports.object = {
    name: 'simpleExample',
    description: 'A simple example advanced script',
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

// The React component
const SimpleExample = () => {
    const [count, setCount] = React.useState(0)

    return (
        <div className="p-4 bg-gray-800 rounded-lg">
            <h2 className="text-xl font-bold text-white">Simple Example</h2>
            <div className="mt-4 space-y-4">
                <p className="text-gray-200">Count: {count}</p>
                <button 
                    onClick={() => setCount(count + 1)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    Increment
                </button>
            </div>
        </div>
    )
}

// Export the component as default
exports.default = SimpleExample
