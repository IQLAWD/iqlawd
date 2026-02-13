import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('62.72.46.228', username='root', password='sayalupa')

print("--- RUNNING BUILD DEBUG ---")
# Run build and capture EVERYTHING
stdin, stdout, stderr = ssh.exec_command("cd /root/iq_lawd_v2/frontend_src && npx next build")
out = stdout.read().decode()
err = stderr.read().decode()

print("STDOUT:", out)
print("STDERR:", err)

ssh.close()
