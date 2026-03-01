import sys

with open("pdf_processor.py", "r") as f:
    content = f.read()

search = """            width = ur_x - ll_x
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
            split_writer.add_page(rp)"""

replace = """            width = ur_x - ll_x
            height = ur_y - ll_y

            # Determine number of splits based on aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            num_splits = 4 if aspect_ratio > 2.1 else 2

            segment_width = width / num_splits

            for j in range(num_splits):
                segment_ll_x = ll_x + (j * segment_width)
                segment_ur_x = segment_ll_x + segment_width

                segment_rect = RectangleObject((segment_ll_x, ll_y, segment_ur_x, ur_y))

                sub_page = copy.copy(page)
                sub_page.mediabox = segment_rect
                sub_page.cropbox = segment_rect

                # Purge secondary boxes to prevent viewer overrides
                for box in ['/ArtBox', '/BleedBox', '/TrimBox']:
                    if box in sub_page: sub_page.pop(box)

                split_writer.add_page(sub_page)"""

if search in content:
    content = content.replace(search, replace)
    with open("pdf_processor.py", "w") as f:
        f.write(content)
    print("Successfully patched pdf_processor.py")
else:
    print("Could not find the target string to replace")
