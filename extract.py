import os

# Set the path to your main 'cvs' directory
cvs_dir = 'data/data'  # <-- Change this to your actual path

# Traverse each subdirectory in 'cvs'
for folder_name in os.listdir(cvs_dir):
    folder_path = os.path.join(cvs_dir, folder_name)
    
    if os.path.isdir(folder_path):
        # Get list of all PDFs sorted alphabetically
        pdf_files = sorted(
            [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        )
        
        # Keep only the first 20
        for pdf_to_delete in pdf_files[20:]:
            try:
                os.remove(os.path.join(folder_path, pdf_to_delete))
                print(f"Deleted: {os.path.join(folder_path, pdf_to_delete)}")
            except Exception as e:
                print(f"Error deleting {pdf_to_delete}: {e}")