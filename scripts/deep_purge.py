import paramiko
import time

HOST = "62.72.46.228"
USER = "root"
PASSWORD = "sayalupa"

def deep_purge_and_rebuild():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD)
    
    print("🧹 Purging all files in root except essential ones...")
    # List of files to KEEP
    keep = ["app", "public", "node_modules", "package.json", "package-lock.json", "next.config.mjs", "tailwind.config.ts", "postcss.config.js", "tsconfig.json", ".next"]
    
    stdin, stdout, stderr = ssh.exec_command("ls /root/iq_lawd_v2/frontend_src")
    files = stdout.read().decode().split()
    
    for f in files:
        if f not in keep:
            print(f"   -> Removing {f}")
            ssh.exec_command(f"rm -rf /root/iq_lawd_v2/frontend_src/{f}")
    
    print("🔥 Killing processes...")
    ssh.exec_command("pkill -9 -f node; pkill -9 -f next; fuser -k 3005/tcp")
    time.sleep(2)
    
    print("🏗️ Rebuilding...")
    cmd = "cd /root/iq_lawd_v2/frontend_src && npm run build"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    
    print("🚀 Starting...")
    ssh.exec_command("cd /root/iq_lawd_v2/frontend_src && nohup ./node_modules/.bin/next start -p 3005 -H 0.0.0.0 > frontend.log 2>&1 &")
    
    ssh.close()

if __name__ == "__main__":
    deep_purge_and_rebuild()
