import os

def generate_tree(path='.', prefix=''):
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return  # Skip directories we can't access
    
    # Filter out unwanted directories/files
    ignored_items = ['venv', 'data', '__pycache__', '.git', 'node_modules']
    entries = [e for e in entries if e not in ignored_items]

    for index, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = '└── ' if index == len(entries) - 1 else '├── '
        print(prefix + connector + entry)
        
        # Only recurse into directories that are not in ignored list
        if os.path.isdir(full_path) and entry not in ignored_items:
            extension = '    ' if index == len(entries) - 1 else '│   '
            generate_tree(full_path, prefix + extension)

if __name__ == '__main__':
    print(".")
    generate_tree()