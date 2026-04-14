import subprocess

def run_batch(path, cwd):
    try:
        subprocess.run([path], cwd=cwd, check=True, shell=True)
        return True
    except:
        return False