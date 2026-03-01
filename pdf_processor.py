import os
import copy
import zipfile
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from pdf2image import convert_from_path

def process_pdf(input_path, output_path, page_range=None, output_format="pdf"):
    """
    Split each page of the PDF into two vertical halves using pypdf.
    Robust handling of offsets and secondary boxes.

    Args:
        input_path (str): Path to the source PDF.
        output_path (str): Path to save the processed PDF.
        page_range (str): Optional string range.
        output_format (str): "pdf" or "images".

    Returns:
        tuple: (bool, str) - Success status and result path.
    """
    try:
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            return False, "PDF is encrypted."

        total_pages = len(reader.pages)
        target_indices = []
        if page_range:
            try:
                for part in page_range.replace(" ", "").split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        target_indices.extend(range(start - 1, end))
                    else:
                        target_indices.append(int(part) - 1)
                target_indices = sorted(list(set([p for p in target_indices if 0 <= p < total_pages])))
            except Exception as e:
                return False, f"Invalid range format: {str(e)}"
        else:
            target_indices = list(range(total_pages))

        if not target_indices:
            return False, "No valid pages selected."

        split_writer = PdfWriter()
        for i in target_indices:
            page = reader.pages[i]

            # Determine the effective boundary for splitting
            # Use cropbox if it differs from mediabox, as it defines the visible area
            source_box = page.cropbox if page.cropbox else page.mediabox

            ll_x = float(source_box.left)
            ll_y = float(source_box.bottom)
            ur_x = float(source_box.right)
            ur_y = float(source_box.top)

            width = ur_x - ll_x
            height = ur_y - ll_y
            mid_x = ll_x + (width / 2)

            # Define split rectangles
            left_rect = RectangleObject((ll_x, ll_y, mid_x, ur_y))
            right_rect = RectangleObject((mid_x, ll_y, ur_x, ur_y))

            # Left Half
            lp = copy.copy(page)
            lp.mediabox = left_rect
            lp.cropbox = left_rect
            # Purge secondary boxes to prevent viewer overrides
            for box in ['/ArtBox', '/BleedBox', '/TrimBox']:
                if box in lp: lp.pop(box)
            split_writer.add_page(lp)

            # Right Half
            rp = copy.copy(page)
            rp.mediabox = right_rect
            rp.cropbox = right_rect
            for box in ['/ArtBox', '/BleedBox', '/TrimBox']:
                if box in rp: rp.pop(box)
            split_writer.add_page(rp)

        for page in split_writer.pages:
            page.compress_content_streams()

        if output_format == "pdf":
            with open(output_path, "wb") as f:
                split_writer.write(f)
            return True, output_path

        elif output_format == "images":
            temp_pdf_path = f"{output_path}_tmp.pdf"
            with open(temp_pdf_path, "wb") as f:
                split_writer.write(f)

            try:
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
                return False, f"Image conversion error: {str(e)}"

        return False, "Format error."

    except Exception as e:
        print(f"Processor Error: {e}")
        return False, str(e)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_pdf(sys.argv[1], "output_test.pdf")
