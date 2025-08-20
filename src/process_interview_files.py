# Read docx files
from docx import Document
import glob

def read_docx_file(file_path):
    doc = Document(file_path)
    return doc

def main():
    files = glob.glob("interview_files/*.docx")
    print(files)
    
    file = files[1]
    doc = read_docx_file(file)
    paragraphs = doc.paragraphs
    for paragraph in paragraphs:
        print(paragraph.text)

        print("-"*100)


if __name__ == "__main__":
    main()