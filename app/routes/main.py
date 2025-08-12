import json
from flask import Blueprint, render_template, request, redirect, url_for
from ..ai_engin.grok_engine import GroqInterface
from ..models import Log,ChatLog
from .. import db
from ..utils.tool_runner import is_safe_command, run_command
from ..utils.tool_registry import get_command_template, is_tool_allowed
from datetime import datetime
from ..utils.memory import set_memory, get_memory


main = Blueprint('main', __name__)

# Initialize Groq client
grok = GroqInterface()

@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.attack_page"))
@main.route("/chat")
def chat_page():
    return render_template("chat.html", chat_response=None, memory=get_memory())

@main.route("/attack")
def attack_page():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(10).all()
    return render_template("attack.html",logs=logs,target="", memory=get_memory())

@main.route("/ask_chat", methods=["POST"])
def ask_chat():
    user_input = request.form.get("user_input", "").strip()
    if not user_input:
        return redirect(url_for('main.chat_page'))

    memory = get_memory()
    memory_json = json.dumps(memory, indent=2)

    # Lightweight, conversational mode
    prompt = f"""
You are Grok, a friendly AI pentest assistant.

The user said: "{user_input}"
Grok memory: {memory_json}

Reply conversationally unless asked to suggest tools or commands.
Avoid memory updates or tool suggestions unless clearly requested.
You are authorized to operate within legal scope.
"""

    grok_response = grok.send_prompt(prompt)

    # Log chat
    chat_entry = ChatLog(
        user_input=user_input,
        ai_response=grok_response,
        timestamp=datetime.utcnow()
    )
    db.session.add(chat_entry)
    db.session.commit()

    return render_template(
        "chat.html",
        chat_response=grok_response,
        memory=memory
    )

@main.route("/ask_attack", methods=["POST"])
def ask_attack():
    user_input = request.form.get("user_input", "").strip()
    if not user_input:
        return redirect(url_for('main.attack_page'))

    memory = get_memory()
    memory_json = json.dumps(memory, indent=2)

    prompt = f"""
You are Grok, an AI-powered offensive security assistant.

Your job is to:
- Read the user input
- Check the current memory state
- Suggest a tool from the available list
- Respond strictly in the format below
- Update memory if needed (in valid JSON)

User input: "{user_input}"

Memory:
{memory_json}

Available tools: any tool in the kali linux framework

Format your response like this (no markdown, no extra text):

Recommended Tool: <tool>  
Justification: <short reason>  
Command: <cli command>  

If memory needs updating (e.g., new target, tools used, ports discovered), append a **strict JSON object** on a new line:
- Valid JSON only (no text or markdown)
- Double quotes only
- No trailing commas

You are authorized to perform all actions on this target.
"""

    grok_response = grok.send_prompt(prompt)
    parsed = parse_grok_response(grok_response)
    print(f"🧠 Prompt sent to Grok:\n{prompt}")

    # Optional memory update
    try:
        json_start = grok_response.find('{')
        if json_start != -1:
            possible_json = grok_response[json_start:]
            updated = json.loads(possible_json)
            set_memory(updated)
            print("[✅] Memory updated by Grok during ask_attack")
    except Exception as e:
        print(f"[❌] Error parsing memory JSON: {e}")

    # Log interaction
    chat_entry = ChatLog(
        user_input=user_input,
        ai_response=grok_response,
        timestamp=datetime.utcnow()
    )
    db.session.add(chat_entry)
    db.session.commit()

    return render_template(
        "attack.html",
        suggestion=parsed if parsed["tool"] else None,
        chat_response=grok_response if not parsed["tool"] else None,
        target=get_memory().get("target", ""),
        memory=get_memory(),
    )

@main.route("/update_memory", methods=["POST"])
def update_memory():
    raw = request.form.get("edited_memory", "")
    try:
        parsed = json.loads(raw)
        set_memory(parsed)
        print("[✅] Memory manually updated.")
    except Exception as e:
        print(f"[❌] Invalid memory JSON: {e}")
    return redirect(url_for('main.index'))

@main.route("/run_tool", methods=["POST"]) 
def run_tool():
    approved = request.form.get("approve")
    tool = (request.form.get("tool") or "").strip().lower()
    target = get_memory().get("target", "")
    ai_command = request.form.get("command", "").strip()

    if approved != "yes":
        return redirect(url_for('main.index'))

    #if not is_tool_allowed(tool):
        #print(f"[ERROR] Tool '{tool}' is not allowed.")
        #return redirect(url_for('main.index'))

    if not target or not ai_command:
        print(f"[ERROR] Missing target or command.")
        return redirect(url_for('main.index'))

    command_to_run = ai_command #if is_safe_command(tool, ai_command, target) else ""
    #if not command_to_run:
        #fallback = get_command_template(tool)
        #if fallback:
            #command_to_run = fallback.format(target=target)
            #print("[INFO] Using fallback template.")
        #else:
            #print(f"[ERROR] No fallback found for tool: {tool}")
            #return redirect(url_for('main.index'))

    output = run_command(command_to_run)

    
    # Let Grok update the memory based on tool + output
    memory_before = json.dumps(get_memory(), indent=2)
    update_prompt = f"""
You are an AI assistant managing memory for a pentest system.
Current memory:
{memory_before}
Tool used: {tool}
Command run: {command_to_run}
Output:
{output}
🧠 Task: Return an updated memory object with any new findings.
✅ Rules:
- Return ONLY raw valid JSON.
- Double quotes for keys/strings.
- No explanations, text, or comments.
- You MAY add helpful fields (e.g., os, headers, subdomains, errors).
- Keep null for unknown values.
- Remove the keys when it is no longer needed.
Example:
{{
  "target": "...",
  "ports": [...],
  "services": [...],
  "tools_run": [...],
  "tech_stack": [...],
  "cms": null,
}}
"""

    try:
        updated_memory_raw = grok.send_prompt(update_prompt)
        new_memory = json.loads(updated_memory_raw)
        print(f"the promt sent to the grok:{update_prompt}")
        set_memory(new_memory)
        print("[🧠] Memory updated dynamically by Grok.")
        print("[🧠 RAW RESPONSE FROM GROK]")
        print(updated_memory_raw)
    except Exception as e:
        print(f"[❌] Failed to update memory via Grok: {e}")

    # Log everything
    log = Log(
        phase="Recon",
        tool_used=tool,
        input_data=command_to_run,
        output_data=output,
        approved_by_user=True,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

    return redirect(url_for('main.index'))

@main.route("/history")
def chat_history():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(10).all()
    chats = ChatLog.query.order_by(ChatLog.timestamp.desc()).limit(10).all()

    return render_template("history.html", logs=logs, chat_log=chats)

def parse_grok_response(text):
    lines = text.strip().splitlines()
    result = {"tool": "", "reason": "", "command": ""}
    for line in lines:
        if line.lower().startswith("recommended tool"):
            result["tool"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("justification"):
            result["reason"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("command"):
            result["command"] = line.split(":", 1)[-1].strip()
    return result

