import fitz
import os

def process_pdf(input_path, output_path):
    """
    Split each page of the PDF into two vertical halves and compress the result.

    Args:
        input_path (str): Path to the source PDF.
        output_path (str): Path to save the processed PDF.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Open source document
        src = fitz.open(input_path)

        # Check if the document is encrypted
        if src.is_encrypted:
            print(f"Error: {input_path} is encrypted.")
            return False

        # Create a new document for the split pages
        dest = fitz.open()

        for page in src:
            # Get original page dimensions (MediaBox)
            rect = page.rect
            width = rect.width
            height = rect.height
            mid_x = width / 2

            # Define rectangles for the left and right halves
            # Rect(x0, y0, x1, y1)
            left_rect = fitz.Rect(0, 0, mid_x, height)
            right_rect = fitz.Rect(mid_x, 0, width, height)

            # 1. Create left page in destination
            # We create a page with the size of the half-page
            new_page_left = dest.new_page(width=mid_x, height=height)
            # Render the original page into the new page's rect, using left_rect as a clipping mask
            new_page_left.show_pdf_page(new_page_left.rect, src, page.number, clip=left_rect)

            # 2. Create right page in destination
            new_page_right = dest.new_page(width=mid_x, height=height)
            # Render the original page into the new page's rect, using right_rect as a clipping mask
            new_page_right.show_pdf_page(new_page_right.rect, src, page.number, clip=right_rect)

        # Save with high-level optimization
        # garbage=4: Remove unused objects and duplicate objects
        # deflate=True: Compress streams
        # clean=True: Clean up document structure
        dest.save(
            output_path,
            garbage=4,
            deflate=True,
            clean=True
        )

        src.close()
        dest.close()
        return True
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False

if __name__ == "__main__":
    # Simple test if run directly
    import sys
    if len(sys.argv) > 1:
        process_pdf(sys.argv[1], "output_test.pdf")
