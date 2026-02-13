import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("62.72.46.228", username="root", password="sayalupa")
    
    # 1. Kill everything to be sure
    print("🧹 Cleaning up...")
    ssh.exec_command("pm2 delete all")
    ssh.exec_command("pkill -f python3")
    ssh.exec_command("rm -rf /root/iq_lawd_v2/frontend_src/.next")
    
    # 2. Start API
    # Ensure it uses the one in /root/iqlawd/backend
    print("🚀 Starting API...")
    ssh.exec_command("cd /root/iqlawd/backend && pm2 start 'python3 -m iq_lawd.api.server' --name iqlawd-api")
    
    # 3. Build & Start Frontend
    print("🔨 Building Frontend...")
    stdin, stdout, stderr = ssh.exec_command("cd /root/iq_lawd_v2/frontend_src && npm run build")
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status == 0:
        print("✅ Frontend Built!")
        ssh.exec_command("cd /root/iq_lawd_v2/frontend_src && pm2 start 'npx next start -p 3005' --name iqlawd-frontend")
        print("✨ All systems restarted!")
    else:
        print("❌ Frontend Build Failed!")
        print(stderr.read().decode())

finally:
    ssh.close()
