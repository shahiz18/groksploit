# app/utils/tool_registry.py

WHITELISTED_TOOLS = {
    "nmap": "nmap -sV -top-ports 100 {target}",
    "subfinder": "subfinder -d {target}",
    "httpx": "httpx -silent -u https://{target}",
    "whatweb": "whatweb {target}",
    "theharvester": "theHarvester -d {target} -b google",
    "zap":"zap-full-scan.py -t {target}"
}

def get_command_template(tool):
    return WHITELISTED_TOOLS.get(tool)

def is_tool_allowed(tool):
    if not tool:
        return False
    return tool.strip().lower() in WHITELISTED_TOOLS
