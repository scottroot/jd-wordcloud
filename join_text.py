from pathlib import Path

def join_job_descriptions(directory: str = 'job_descriptions') -> str:
    """
    Combines text from all job description files in the specified directory.

    Args:
        directory (str): Path to the directory containing job description files

    Returns:
        str: Combined text from all job description files
    """
    combined_text = []

    # Get all .txt files in the directory
    for file_path in sorted(Path(directory).glob('*.txt')):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Add a header with the filename
                # combined_text.append(f"\n{'='*80}\n")
                # combined_text.append(f"File: {file_path.name}\n")
                # combined_text.append(f"{'='*80}\n\n")
                # Add the file contents
                combined_text.append(f.read())
                # combined_text.append("\n\n")
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")

    return ''.join(combined_text)

if __name__ == "__main__":
    # Print the combined text
    print(join_job_descriptions())
