from devagent.rag.scanner import scan_repo

if __name__ == '__main__':
    repo_path = "/Users/mac/Documents/DevAgent/src/devagent"
    files = scan_repo(repo_path)
    print(files[:5])