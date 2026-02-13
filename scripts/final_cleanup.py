import os
import shutil

def final_cleanup():
    # Rename deploy_master.py to deploy.py
    if os.path.exists("deploy_master.py"):
        if os.path.exists("deploy.py"):
            os.remove("deploy.py")
        os.rename("deploy_master.py", "deploy.py")
        print("✅ Renamed deploy_master.py to deploy.py")
        
    # Delete temporary scripts
    temps = [
        "clean_local.py",
        "kill_zombies.py",
        "verify_remote_server.py",
        "deploy_cleanup.py",
        "deploy_fix_assets.py"
    ]
    
    for t in temps:
        if os.path.exists(t):
            try:
                os.remove(t)
                print(f"🗑️ Deleted {t}")
            except Exception as e:
                print(f"❌ Error deleting {t}: {e}")

if __name__ == "__main__":
    final_cleanup()
