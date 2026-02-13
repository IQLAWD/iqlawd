import os
import shutil

def organize():
    root = r"z:\CODINGAN\IQLAWD"
    scripts_dir = os.path.join(root, "scripts")
    
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
        print(f"Created {scripts_dir}")

    # Files to keep in root
    keep = [
        "iq_lawd",
        "frontend_src",
        ".env",
        ".env.example",
        ".gitignore",
        "requirements.txt",
        "README.md",
        "scripts",
        "logo.jpg",
        "main.py",
        "ecosystem.config.js",
        "node.zip", # maybe remove this too later
        "portable_node",
        "iqlawd.db", # keep for now, but usually gitignored
        "iqlawd_cache.db"
    ]

    for item in os.listdir(root):
        if item in keep or item.startswith("."):
            continue
            
        src = os.path.join(root, item)
        dst = os.path.join(scripts_dir, item)
        
        try:
            shutil.move(src, dst)
            print(f"Moved {item} to scripts/")
        except Exception as e:
            print(f"Failed to move {item}: {e}")

if __name__ == "__main__":
    organize()
