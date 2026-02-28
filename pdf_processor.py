import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
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
            return False

        for page in reader.pages:
            # Original bounds
            mb = page.mediabox
            width = float(mb.width)
            height = float(mb.height)
            left = float(mb.left)
            bottom = float(mb.bottom)
            mid_x = left + (width / 2)

            # Define the two halves
            left_rect = RectangleObject((left, bottom, mid_x, bottom + height))
            right_rect = RectangleObject((mid_x, bottom, left + width, bottom + height))

            # Left Half
            left_page = copy.copy(page)
            left_page.mediabox = left_rect
            left_page.cropbox = left_rect
            writer.add_page(left_page)

            # Right Half
            right_page = copy.copy(page)
            right_page.mediabox = right_rect
            right_page.cropbox = right_rect
            writer.add_page(right_page)

        # Apply basic compression
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
