import requests

print("Testing /analyze for moltxio...")
try:
    res = requests.post("http://62.72.46.228:8000/analyze", json={"agent_id": "laukiantonson"}, timeout=30)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")

import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.72.46.228', username='root', password='sayalupa')

print("\n--- API LOGS ---")
stdin, stdout, stderr = ssh.exec_command("pm2 logs iqlawd-api --lines 50 --nostream")
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
