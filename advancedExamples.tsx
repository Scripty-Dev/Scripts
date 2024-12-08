// advancedExample.tsx
import React, { useState, useEffect } from 'react'

// Type for our response
type AdvancedScriptResponse = {
  type: 'advanced'
  ui: string
  handler: string
}

// The UI component we'll render
export const UI = () => {
  const [data, setData] = useState<string>('')
  
  return (
    <div className="p-4">
      <h2 className="text-lg font-bold">Advanced Script</h2>
      <div className="mt-4">
        {/* Your UI content */}
      </div>
    </div>
  )
}

// The handler that will run
export const handler = async () => {
  // Background processing code
}

// The function that ScriptAgent calls
export const func = async (): Promise<AdvancedScriptResponse> => {
  return {
    type: 'advanced',
    ui: UI.toString(), // Convert UI component to string
    handler: handler.toString() // Convert handler to string
  }
}

// The required object export for ScriptAgent
export const object = {
  name: 'advancedExample',
  description: 'An example advanced script with UI.',
  parameters: {
    type: 'object',
    properties: {},
    required: []
  }
}
