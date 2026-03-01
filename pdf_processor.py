import os
import copy
import zipfile
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from pdf2image import convert_from_path

def process_pdf(input_path, output_path, page_range=None, output_format="pdf"):
    """
    Split each page of the PDF into two vertical halves using pypdf.

    Args:
        input_path (str): Path to the source PDF.
        output_path (str): Path to save the processed PDF.
        page_range (str): Optional string range like "1-5", "1,3,5", or "1-5,7".
        output_format (str): "pdf" or "images".

    Returns:
        tuple: (bool, str) - Success status and path to the resulting file.
    """
    try:
        reader = PdfReader(input_path)

        if reader.is_encrypted:
            return False, "PDF is encrypted."

        # Parse page range
        total_pages = len(reader.pages)
        target_indices = []
        if page_range:
            try:
                # Basic range parser: handles "1-3, 5, 7-10"
                for part in page_range.replace(" ", "").split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        target_indices.extend(range(start - 1, end))
                    else:
                        target_indices.append(int(part) - 1)

                # Filter and deduplicate indices
                target_indices = sorted(list(set([p for p in target_indices if 0 <= p < total_pages])))
            except Exception as e:
                return False, f"Invalid page range format: {str(e)}"
        else:
            target_indices = list(range(total_pages))

        if not target_indices:
            return False, "No valid pages found in selected range."

        # Process pages into a split PDF first
        split_writer = PdfWriter()
        for i in target_indices:
            page = reader.pages[i]
            mb = page.mediabox
            width = float(mb.width)
            height = float(mb.height)
            left = float(mb.left)
            bottom = float(mb.bottom)
            mid_x = left + (width / 2)

            left_rect = RectangleObject((left, bottom, mid_x, bottom + height))
            right_rect = RectangleObject((mid_x, bottom, left + width, bottom + height))

            # Left Half
            lp = copy.copy(page)
            lp.mediabox = left_rect
            lp.cropbox = left_rect
            split_writer.add_page(lp)

            # Right Half
            rp = copy.copy(page)
            rp.mediabox = right_rect
            rp.cropbox = right_rect
            split_writer.add_page(rp)

        # Apply basic compression
        for page in split_writer.pages:
            page.compress_content_streams()

        # Handle output formats
        if output_format == "pdf":
            with open(output_path, "wb") as f:
                split_writer.write(f)
            return True, output_path

        elif output_format == "images":
            temp_pdf_path = f"{output_path}_split_temp.pdf"
            with open(temp_pdf_path, "wb") as f:
                split_writer.write(f)

            try:
                # Convert PDF pages to JPEGs
                images = convert_from_path(temp_pdf_path)
                zip_filename = output_path.replace(".pdf", ".zip")

                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for idx, img in enumerate(images):
                        img_name = f"page_{idx+1:03d}.jpg"
                        img.save(img_name, "JPEG", quality=85)
                        zipf.write(img_name)
                        os.remove(img_name)

                os.remove(temp_pdf_path)
                return True, zip_filename
            except Exception as e:
                if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)
                return False, f"Failed to convert PDF to images: {str(e)}"

        return False, "Unsupported output format."

    except Exception as e:
        print(f"Error in process_pdf: {e}")
        return False, str(e)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_pdf(sys.argv[1], "output_test.pdf")
