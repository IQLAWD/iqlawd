import paramiko
import time
import json

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def deploy_master():
    print(f"🔌 Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD)
        
        print("\n🚀 IQLAWD MASTER DEPLOYMENT (Clean & Restart) 🚀\n")
        
        # 1. Force Kill Everything
        print("💀 Step 1: Killing ALL existing processes...")
        ssh.exec_command("pm2 delete all") # Delete everything from PM2
        ssh.exec_command("pm2 save")
        ssh.exec_command("pkill -f uvicorn")
        ssh.exec_command("pkill -f python")
        ssh.exec_command("pkill -f next")
        ssh.exec_command("pkill -f node")
        time.sleep(2)
        
        # 2. Upload Backend Code (Server.py) - Just to be safe
        print("📦 Step 2: Uploading Verified server.py...")
        sftp = ssh.open_sftp()
        sftp.put("z:/CODINGAN/IQLAWD/iq_lawd/api/server.py", "/root/iqlawd/backend/iq_lawd/api/server.py")
        sftp.close()
        
        # 3. Clean Remote Tmp Files (Quick check)
        print("🧹 Step 3: Cleaning remote temporary files...")
        # Not deleting everything, just ensuring clean state for logs
        ssh.exec_command("rm -rf /root/.pm2/logs/*")
        
        # 4. Start Backend
        print("🔥 Step 4: Starting Backend API (fresh)...")
        # Direct PM2 start for backend
        cmd_backend = "cd /root/iqlawd/backend && pm2 start 'uvicorn iq_lawd.api.server:app --host 0.0.0.0 --port 8000' --name iqlawd-api"
        stdin, stdout, stderr = ssh.exec_command(cmd_backend)
        print(stdout.read().decode())
        
        # 5. Start Frontend
        print("🎨 Step 5: Starting Frontend UI (fresh)...")
        # Ensure we are in the RIGHT directory and it's built
        # We need to make sure 'npm start' uses the port we want
        # And we need to rebuild if we suspect the build is stale
        print("   Rebuilding to be safe...")
        ssh.exec_command("cd /root/iqlawd/frontend && npm run build")
        
        cmd_frontend = "cd /root/iqlawd/frontend && pm2 start 'npm start -- -p 3005' --name iqlawd-ui" 
        stdin, stdout, stderr = ssh.exec_command(cmd_frontend)
        print(stdout.read().decode())
        
        # Save PM2 list
        ssh.exec_command("pm2 save")
        
        print("\n✅ Master Deployment & Restart Complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_master()
