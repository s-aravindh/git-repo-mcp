from fastmcp import FastMCP
import os

mcp = FastMCP("git_repo_mcp")

# Configuration - can be set via environment variables or defaults
DEFAULT_REPO_PATH = "/Users/aravindh/Documents/GitHub/unified-llm"
repo_folder = os.getenv("GIT_REPO_PATH", DEFAULT_REPO_PATH)

@mcp.tool()
def overview() -> str:
    """Get repository overview: README content and project structure"""
    repo_name = os.path.basename(repo_folder)
    
    # Get README content
    readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md', 'readme.txt']
    readme_content = None
    
    for readme_file in readme_files:
        try:
            with open(f"{repo_folder}/{readme_file}", "r") as f:
                readme_content = f.read()
            break
        except FileNotFoundError:
            continue
    
    # Get project structure
    structure = [f"Repository: {repo_name}\n"]
    
    for root, dirs, files in os.walk(repo_folder):
        # Skip hidden directories and common build/cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
            '__pycache__', 'node_modules', '.git', 'venv', 'env', 'build', 'dist', '.pytest_cache'
        ]]
        
        level = root.replace(repo_folder, '').count(os.sep)
        if level >= 3:  # Max depth 3
            dirs.clear()
            continue
            
        indent = '  ' * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        
        sub_indent = '  ' * (level + 1)
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                structure.append(f"{sub_indent}{file}")
    
    project_structure = '\n'.join(structure)
    
    # Combine results
    result = f"# REPOSITORY OVERVIEW\n\n## Project Structure\n\n{project_structure}\n\n"
    
    if readme_content:
        result += f"## README Content\n\n{readme_content}"
    else:
        result += f"## README Content\n\nNo README file found in repository: {repo_name}"
    
    return result

@mcp.tool()
def get_files_from_folder(folder_path: str) -> str:
    """Get all files from a specific folder in the repository
    
    Args:
        folder_path: Relative path to the folder from repository root (e.g., 'src', 'docs', 'examples')
    """
    try:
        full_path = os.path.join(repo_folder, folder_path)
        
        # Security check - ensure folder is within repo
        if not os.path.abspath(full_path).startswith(os.path.abspath(repo_folder)):
            return "Error: Folder path outside repository"
        
        if not os.path.exists(full_path):
            return f"Folder not found: {folder_path}"
        
        if not os.path.isdir(full_path):
            return f"Path is not a folder: {folder_path}"
        
        files_list = []
        
        # List all files in the folder (not recursive)
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            if os.path.isfile(item_path):
                files_list.append(f"📄 {item}")
            elif os.path.isdir(item_path):
                files_list.append(f"📁 {item}/")
        
        if files_list:
            return f"Contents of folder '{folder_path}':\n\n" + '\n'.join(sorted(files_list))
        else:
            return f"Folder '{folder_path}' is empty"
    
    except Exception as e:
        return f"Error reading folder {folder_path}: {str(e)}"

@mcp.tool()
def get_file(file_path: str) -> str:
    """Get the content of any specific file in the repository
    
    Args:
        file_path: Relative path to the file from repository root (e.g., 'src/main.py', 'docs/api.md')
    """
    try:
        full_path = os.path.join(repo_folder, file_path)
        
        # Security check - ensure file is within repo
        if not os.path.abspath(full_path).startswith(os.path.abspath(repo_folder)):
            return "Error: File path outside repository"
        
        if not os.path.exists(full_path):
            return f"File not found: {file_path}"
        
        if not os.path.isfile(full_path):
            return f"Path is not a file: {file_path}"
        
        with open(full_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        return f"# {file_path}\n\n{content}"
    
    except UnicodeDecodeError:
        return f"Error: Cannot read file {file_path} (binary file or encoding issue)"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")