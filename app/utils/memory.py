memory = {
    "target": None,
    "ports": [],
    "services": [],
    "tech_stack": [],
    "cms": None,
    "vulns": [],
    "phase": "Recon",
    "tools_run": []
}


def get_memory():
    return memory

def set_memory(new_data):
    global memory
    for key, value in new_data.items():
        memory[key] = value

def reset_memory():
    global memory
    memory = {
        "target": None,
        "ports": [],
        "services": [],
        "tech_stack": [],
        "cms": None,
        "vulns": [],
        "phase": "Recon",
        "tools_run": []
    }
