"""
prepare_documents.py
Helper script to prepare PDF documents for SVGelona
"""

import os
import shutil
from pathlib import Path

def setup_documents_folder():
    """Create documents folder and show instructions"""
    
    documents_path = "documents"
    
    # Create folder if it doesn't exist
    os.makedirs(documents_path, exist_ok=True)
    
    print("="*60)
    print("📚 SVGelona - Document Preparation")
    print("="*60)
    print()
    print(f"Documents folder created at: {os.path.abspath(documents_path)}")
    print()
    print("📌 INSTRUCTIONS:")
    print("1. Copy your PDF files into the 'documents' folder")
    print("2. Suggested PDFs for SVGelona:")
    print("   - 600-cell.pdf (properties of the 600-cell)")
    print("   - angular_defect.pdf (explanation of 6.8° defect)")
    print("   - riemann_zeros.pdf (first 100 zeros)")
    print("   - symmetries.pdf (8 symmetries of Γ_R(s))")
    print("   - consciousness_theory.pdf (your consciousness theory)")
    print()
    print("3. PDF files can be in any language (Spanish/English)")
    print("4. The system will automatically index them")
    print()
    print("📊 Current PDFs in folder:")
    
    pdf_files = list(Path(documents_path).glob("*.pdf"))
    pdf_files.extend(Path(documents_path).glob("*.PDF"))
    
    if pdf_files:
        for pdf in pdf_files:
            size = pdf.stat().st_size / 1024  # KB
            print(f"   ✅ {pdf.name} ({size:.1f} KB)")
    else:
        print("   ⚠️ No PDF files found yet")
    
    print()
    print("="*60)

if __name__ == "__main__":
    setup_documents_folder()