import paramiko

HOST = "62.72.46.228"
USER = "root"
PASS = "sayalupa"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)
sftp = ssh.open_sftp()

# Upload the updated page.tsx
print("📤 Uploading page.tsx with X & GitHub buttons...")
sftp.put(r"z:\CODINGAN\IQLAWD\frontend_src\app\page.tsx", "/root/iqlawd/frontend/app/page.tsx")
print("✅ Uploaded!")
sftp.close()

# Rebuild and restart
print("🔧 Rebuilding frontend...")
stdin, stdout, stderr = ssh.exec_command("cd /root/iqlawd/frontend && npm run build && pm2 restart iqlawd-frontend", timeout=120)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err[-500:])

print("🚀 DONE! X & GitHub buttons are now live.")
ssh.close()
