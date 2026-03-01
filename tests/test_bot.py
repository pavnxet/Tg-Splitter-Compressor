import unittest
import os
from unittest import IsolatedAsyncioTestCase
from pypdf import PdfWriter, PdfReader
from pypdf.generic import RectangleObject
from pdf_processor import process_pdf

class TestBotHandlers(IsolatedAsyncioTestCase):

    def setUp(self):
        # Create a mock 2-up PDF
        self.two_up_path = "mock_2up.pdf"
        writer_2up = PdfWriter()
        page_2up = writer_2up.add_blank_page(width=400, height=250) # Aspect ratio 400/250 = 1.6
        with open(self.two_up_path, "wb") as f:
            writer_2up.write(f)

        # Create a mock 4-up PDF
        self.four_up_path = "mock_4up.pdf"
        writer_4up = PdfWriter()
        page_4up = writer_4up.add_blank_page(width=800, height=250) # Aspect ratio 800/250 = 3.2
        with open(self.four_up_path, "wb") as f:
            writer_4up.write(f)

        self.output_pdf = "output_mock.pdf"

    def tearDown(self):
        for path in [self.two_up_path, self.four_up_path, self.output_pdf]:
            if os.path.exists(path):
                os.remove(path)

    async def test_process_pdf_two_up(self):
        success, res_path = process_pdf(self.two_up_path, self.output_pdf, output_format="pdf")
        self.assertTrue(success)
        self.assertEqual(res_path, self.output_pdf)

        # Verify it split into 2 pages
        reader = PdfReader(self.output_pdf)
        self.assertEqual(len(reader.pages), 2)

        # Verify dimensions of output pages
        page1 = reader.pages[0]
        self.assertAlmostEqual(float(page1.mediabox.width), 200.0)

    async def test_process_pdf_four_up(self):
        success, res_path = process_pdf(self.four_up_path, self.output_pdf, output_format="pdf")
        self.assertTrue(success)
        self.assertEqual(res_path, self.output_pdf)

        # Verify it split into 4 pages
        reader = PdfReader(self.output_pdf)
        self.assertEqual(len(reader.pages), 4)

        # Verify dimensions of output pages
        page1 = reader.pages[0]
        self.assertAlmostEqual(float(page1.mediabox.width), 200.0)

if __name__ == '__main__':
    unittest.main()
