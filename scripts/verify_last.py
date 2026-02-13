import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("62.72.46.228", username="root", password="sayalupa")
    
    # Check headers
    stdin, stdout, stderr = ssh.exec_command("curl -I http://localhost:8000/agents/search?q=Fred")
    print("--- Headers ---")
    print(stdout.read().decode())
    
    # Check page.tsx content (just in case)
    stdin, stdout, stderr = ssh.exec_command("grep 'council' /root/iq_lawd_v2/frontend_src/app/page.tsx | head -n 1")
    print("--- Grep page.tsx ---")
    print(stdout.read().decode())

finally:
    ssh.close()
