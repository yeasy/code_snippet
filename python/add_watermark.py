import io
import argparse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, black


def add_watermark(pdf_input_path, watermark_text, pdf_output_path):
	# create a pdf reader
	input_pdf = PdfReader(pdf_input_path)
	output_pdf = PdfWriter()

	# create a PDF canvas
	packet = io.BytesIO()
	can = canvas.Canvas(packet, pagesize=letter)

	# set transparency to 10%
	fill_color = Color(black.red, black.green, black.blue, alpha=0.1)
	can.setFillColor(fill_color)
	can.setFont("Helvetica", 28)

	# watermark text
	for i in range(100, 600, 200):  # horizontal
		for j in range(100, 900, 300):  # vertical
			can.saveState()
			can.translate(i, j)
			can.rotate(45)
			can.drawString(0, 0, watermark_text)
			can.restoreState()

	can.save()

	# move to the beginning of the packet
	packet.seek(0)
	new_pdf = PdfReader(packet)

	# add watermark
	for i in range(len(input_pdf.pages)):
		page = input_pdf.pages[i]
		if i != 0:  # skip the first page
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
	parser.add_argument("--output", help="Output PDF file",
	                    default="output.pdf")

	args = parser.parse_args()

	add_watermark(args.input, args.watermark, args.output)


if __name__ == "__main__":
	main()
