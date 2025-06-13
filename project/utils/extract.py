import os

# Set the path to your main 'cvs' directory
data_directory = '../data/data'  # <-- Change this to your actual path

# Traverse each subdirectory in 'cvs'
for subdirectory_name in os.listdir(data_directory):
    subdirectory_path = os.path.join(data_directory, subdirectory_name)
    
    if os.path.isdir(subdirectory_path):
        # Get list of all PDFs sorted alphabetically
        all_pdf_files = sorted(
            [filename for filename in os.listdir(subdirectory_path) if filename.lower().endswith('.pdf')]
        )
        
        # Keep only the first 20
        for pdf_file_to_remove in all_pdf_files[19:]:
            try:
                os.remove(os.path.join(subdirectory_path, pdf_file_to_remove))
                print(f"Deleted: {os.path.join(subdirectory_path, pdf_file_to_remove)}")
            except Exception as error:
                print(f"Error deleting {pdf_file_to_remove}: {error}")