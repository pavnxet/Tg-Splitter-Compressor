import os
from pypdf import PdfReader, PdfWriter
import copy

def process_pdf(input_path, output_path):
    """
    Split each page of the PDF into two vertical halves using pypdf.
    Optimized for Termux (Pure Python).

    Args:
        input_path (str): Path to the source PDF.
        output_path (str): Path to save the processed PDF.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        if reader.is_encrypted:
            # We don't support encrypted PDFs in this simple version
            return False

        for page in reader.pages:
            # Get original bounds
            mb = page.mediabox
            width = mb.width
            height = mb.height
            mid_x = mb.left + (width / 2)

            # Left Page
            # We must use a copy or similar approach as we manipulate the mediabox
            # In pypdf, we can add the same page twice and crop each

            # Left Half
            left_page = copy.copy(page)
            left_page.mediabox.right = mid_x
            writer.add_page(left_page)

            # Right Half
            right_page = copy.copy(page)
            right_page.mediabox.left = mid_x
            writer.add_page(right_page)

        # Apply basic compression
        # pypdf can compress content streams
        for page in writer.pages:
            page.compress_content_streams()

        # Save the result
        with open(output_path, "wb") as f:
            writer.write(f)

        return True
    except Exception as e:
        print(f"Error processing PDF with pypdf: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_pdf(sys.argv[1], "output_test.pdf")
