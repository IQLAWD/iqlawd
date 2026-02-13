import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("62.72.46.228", username="root", password="sayalupa")
    
    commands = [
        "pm2 delete all",
        "pkill -f python3",
        "pkill -f next",
        
        # Backend Clean
        "grep 'CORSMiddleware' /root/iqlawd/backend/iq_lawd/api/server.py",
        "cd /root/iqlawd/backend && export PYTHONPATH=$PYTHONPATH:. && pm2 start 'python3 iq_lawd/api/server.py' --name iqlawd-api",
        
        # Frontend Clean
        "cd /root/iq_lawd_v2/frontend_src && rm -rf .next && npm run build",
        "cd /root/iq_lawd_v2/frontend_src && pm2 start 'npx next start -p 3005' --name iqlawd-frontend",
        
        "pm2 save"
    ]
    
    for cmd in commands:
        print(f"\n--- Running: {cmd} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())

finally:
    ssh.close()
