import argparse
from grok_engine import GroqInterface

# CLI argument parser
parser = argparse.ArgumentParser(description="Run Groq in live mode only")
parser.add_argument("--live", action="store_true", help="Run in live mode")
args = parser.parse_args()

if not args.live:
    print("Error: This script only works in live mode. Use --live.")
    exit(1)

# Init GroqInterface in live mode
grok = GroqInterface(model="llama3-70b-8192", live=True)

# Strict JSON-only prompt
sent = """Convert the following Nikto scan output into a valid JSON object.
Do not include any explanation, text, or formatting outside the JSON.  
The JSON keys should reflect the data structure clearly.

Nikto Output:
[01:22:21] - Nikto v2.5.0
[01:22:21] ---------------------------------------------------------------------------
[01:22:21] + Multiple IPs found: 151.101.129.91, 151.101.193.91, 151.101.65.91, 151.101.1.91, 2a04:4e42::347, 2a04:4e42:200::347, 2a04:4e42:400::347, 2a04:4e42:600::347
[01:22:25] + Target IP:          151.101.129.91
[01:22:25] + Target Hostname:    www.myg.in
[01:22:25] + Target Port:        80
[01:22:25] + Start Time:         2025-08-11 01:22:22 (GMT-6)
[01:22:25] ---------------------------------------------------------------------------
[01:22:25] + Server: No banner retrieved
[01:22:27] + /: The anti-clickjacking X-Frame-Options header is not present. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
[01:22:27] + /: Uncommon header 'accept-ch-lifetime' found, with contents: 300.
[01:22:27] + /: Uncommon header 'accept-ch' found, with contents: viewport-width,downlink,dpr,device-memory,ect,rtt.
[01:22:27] + /: Uncommon header 'x-nv-ver' found, with contents: V27.
[01:22:27] + /: The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type. See: https://www.netsparker.com/web-vulnerability-scanner/vulnerabilities/missing-content-type-header/
[01:22:27] + Root page / redirects to: https://www.myg.in/
[01:24:30] + No CGI Directories found (use '-C all' to force check all possible dirs)
[01:25:03] + /: Retrieved via header: 1.1 varnish.
[01:25:03] + /: Retrieved x-served-by header: cache-maa10245-MAA.
[01:25:03] + /: Uncommon header 'x-served-by' found, with contents: cache-maa10245-MAA.
[01:25:45] + No CGI Directories found (use '-C all' to force check all possible dirs)
[01:26:21] + /: Retrieved via header: 1.1 varnish.
[01:26:21] + /: Retrieved x-served-by header: cache-maa10221-MAA.
[01:26:21] + /: Uncommon header 'x-served-by' found, with contents: cache-maa10221-MAA.
[02:21:02] + ERROR: Error limit (20) reached for host, giving up. Last error: opening stream: getaddrinfo problems (Temporary failure in name resolution): Resource temporarily unavailable
[02:21:02] + Scan terminated: 19 error(s) and 8 item(s) reported on remote host
[02:21:02] + End Time:           2025-08-11 02:21:02 (GMT-6) (3736 seconds)
[02:21:02] ---------------------------------------------------------------------------
[02:21:02] + 1 host(s) tested
[02:21:24] + ERROR: Error limit (20) reached for host, giving up. Last error: opening stream: getaddrinfo problems (Temporary failure in name resolution): Resource temporarily unavailable
[02:21:24] + Scan terminated: 20 error(s) and 8 item(s) reported on remote host
[02:21:24] + End Time:           2025-08-11 02:21:24 (GMT-6) (3542 seconds)
[02:21:24] ---------------------------------------------------------------------------
[02:21:24] + 1 host(s) tested
"""

# Send prompt and print response
response = grok.send_prompt(sent)
print("[LIVE]", response)
