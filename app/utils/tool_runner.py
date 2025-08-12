# app/utils/tool_runner.py
import subprocess
import shlex
import time
def is_safe_command(tool, command, target):
    # Simple safety check
    if not command.lower().startswith(tool):
        return False
    if target not in command:
        return False
    if any(bad in command for bad in [';', '&&', '|', '$(', '`']):
        return False
    return True


def run_command(command, idle_timeout=300):
    """
    Run a command with idle timeout (only kill if no output for 'idle_timeout' seconds)
    """
    try:
        process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        last_output_time = time.time()
        output_lines = []

        for line in process.stdout:
            print(f"[{time.strftime('%H:%M:%S')}] {line.strip()}")  # live log to terminal
            output_lines.append(line)
            last_output_time = time.time()

            # If no output for 'idle_timeout' seconds, kill process
            if time.time() - last_output_time > idle_timeout:
                process.kill()
                output_lines.append(f"[ERROR] Tool timed out after {idle_timeout} seconds of inactivity.")
                break

        process.wait()
        return "".join(output_lines)

    except Exception as e:
        return f"[ERROR] Failed to execute command: {e}"

