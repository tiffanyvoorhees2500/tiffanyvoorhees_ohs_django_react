import shutil
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_BUILD_DIR = os.path.join(BASE_DIR, 'frontend', 'build')
DJANGO_REACT_DIR = os.path.join(BASE_DIR, 'react_build')

def copy_build():
    print("Copying from:", REACT_BUILD_DIR)
    print("Copying to:", DJANGO_REACT_DIR)
    
    if not os.path.exists(REACT_BUILD_DIR):
        raise FileNotFoundError(f"React build not found at: {REACT_BUILD_DIR}")
    
    if os.path.exists(DJANGO_REACT_DIR):
        shutil.rmtree(DJANGO_REACT_DIR)
    shutil.copytree(REACT_BUILD_DIR, DJANGO_REACT_DIR)
    
    print(f"✅ React build copied to '{DJANGO_REACT_DIR}'.")

if __name__ == "__main__":
    copy_build()