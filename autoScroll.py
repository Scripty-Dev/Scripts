import sys
import json
import pyautogui
import asyncio

# Configure PyAutoGUI settings
pyautogui.FAILSAFE = True

async def func(args):
    """
    Scrolls down by specified amount
    """
    try:
        scroll_amount = args.get('scroll_amount', 100)
        pyautogui.scroll(-scroll_amount)
        return json.dumps({"message": f"Scrolled down {scroll_amount} pixels"})
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "autoScroll",
    "description": "Scrolls down by specified amount of pixels",
    "parameters": {
        "type": "object",
        "properties": {
            "scroll_amount": {
                "type": "integer",
                "description": "Amount of pixels to scroll (default: 100)",
                "default": 100
            }
        }
    }
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1])
                result = asyncio.run(func(args))
                print(result)
            except Exception as e:
                print(json.dumps({"error": str(e)}))
