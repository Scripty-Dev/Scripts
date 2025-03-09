from typing import Dict, Any

public_description = "A test script created by Scripty"

async def function(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    This is a test script that demonstrates the basic structure.
    
    Args:
        args: Dictionary containing input parameters
        
    Returns:
        Dictionary containing the results
    """
    original_message = args["fein"]
    return {
        "original": original_message,
        "modified": original_message.upper() + "!!!",
        "timestamp": "FEIN TEST EDIT WORKED!"
    }

object = {
    "name": "Test Script",
    "description": "A simple test script to demonstrate Scripty's capabilities",
    "parameters": {
        "type": "object",
        "properties": {
            "fein": {
                "type": "string",
                "description": "The message to display"
            }
        }
    }
} 
