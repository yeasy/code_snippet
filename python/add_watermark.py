# Usage: python3 add_watermark.py --input ~/input.pdf --watermark "watermark"
import io
import argparse
import os
import sys

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, black
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def add_watermark(pdf_input_path, watermark_text, pdf_output_path, change_firstpage):
	# create a pdf reader
	input_pdf = PdfReader(pdf_input_path)
	output_pdf = PdfWriter()

	page = input_pdf.pages[0]

	# Access the media box to get width and height
	page_width = float(page.mediabox.upper_right[0]) - float(
		page.mediabox.lower_left[0])
	page_height = float(page.mediabox.upper_right[1]) - float(
		page.mediabox.lower_left[1])

	# create a PDF canvas for the watermark layer
	packet = io.BytesIO()
	can = canvas.Canvas(packet, pagesize=letter)

	# set transparency to 10%
	fill_color = Color(black.red, black.green, black.blue, alpha=0.1)
	can.setFillColor(fill_color)

	# register TTF fonts
	pdfmetrics.registerFont(TTFont('Songti', '/System/Library/Fonts/Supplemental/Songti.ttc'))
	pdfmetrics.registerFont(TTFont('Helvetica', 'helvetica.ttc'))

	# Function to set appropriate font
	def set_font(can, text):
		if any('\u4e00' <= char <= '\u9fff' for char in text):
			can.setFont("Songti", 28)
		else:
			can.setFont("Helvetica", 28)

	# watermark text
	for i in range(100, int(page_width*0.7), 400):  # horizontal
		for j in range(100, int(page_height*0.7), 300):  # vertical
			can.saveState()
			can.translate(i, j)
			can.rotate(45)
			set_font(can, watermark_text)
			can.drawString(0, 0, watermark_text)
			can.restoreState()

	can.save()

	# move to the beginning of the packet
	packet.seek(0)
	new_pdf = PdfReader(packet)

	# add watermark
	for i in range(len(input_pdf.pages)):
		page = input_pdf.pages[i]
		if change_firstpage or i != 0:  # skip the first page
			page.merge_page(new_pdf.pages[0])
		output_pdf.add_page(page)

	# output to a new pdf file
	with open(pdf_output_path, "wb") as output_file:
		output_pdf.write(output_file)


def main():
	parser = argparse.ArgumentParser(
		description="Add a watermark to a PDF file.")
	parser.add_argument("--input", help="Input PDF file",
						default="input.pdf")
	parser.add_argument("--watermark", help="Watermark text",
						default="Watermark Text")
	parser.add_argument("--output", help="Output PDF file, "
	                                     "default to be the input file with a _marked suffix",
						default="")
	parser.add_argument('--keep-firstpage', action='store_true', default=False,
	                    help='Also add water mark to the first page (default: False)')
	args = parser.parse_args()

	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit(1)

	input = args.input
	output = args.output or f"{os.path.splitext(input)[0]}_marked.pdf"
	add_watermark(input, args.watermark, output, args.keep_firstpage)

	print(f"Output file to {output}")

if __name__ == "__main__":
	main()
