import paramiko
import time

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def verify():
    print(f"🔌 Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD)
        
        print("\n🔍 Checking Logs for 'Requesting Realtime Data'...")
        # Check logs for the signature I added
        stdin, stdout, stderr = ssh.exec_command("grep 'Requesting Realtime Data' /root/.pm2/logs/iqlawd-api-out.log | tail -n 5")
        logs = stdout.read().decode()
        if logs:
            print("✅ LOGS FOUND:")
            print(logs)
        else:
            print("⚠️ No realtime logs found yet.")

        print("\n🧪 Testing NEW Agent 'MOG' (Not in Hardcoded List)...")
        # MOG is a popular meme, likely on Moltbook
        cmd = "curl -X POST http://localhost:8000/verify/MOG"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        resp = stdout.read().decode()
        
        print(f"Response: {resp}")
        
        if '"final_score"' in resp:
            print("✅ MOG Verified! Realtime API is working.")
        else:
            print("⚠️ MOG Verification Failed. API might be limited or agent not found.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    verify()
