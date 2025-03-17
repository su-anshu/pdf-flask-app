import os
import fitz  # PyMuPDF
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

# PDF Processing Function
def highlight_large_qty(pdf_path, output_path):
    doc = fitz.open(pdf_path)

    for page in doc:
        text_blocks = page.get_text("blocks")
        qty_found = False

        for block in text_blocks:
            x0, y0, x1, y1, text, *_ = block

            if "Qty" in text:
                qty_found = True
                continue

            if qty_found:
                qty_found = False
                values = text.split()

                for val in values:
                    if val.isdigit() and int(val) > 1:
                        highlight_box = fitz.Rect(x0, y0, x1, y1)
                        page.draw_rect(highlight_box, color=(1, 0, 0), fill_opacity=0.4)

    doc.save(output_path)

# Serve the HTML Page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Handle File Upload
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    input_pdf = os.path.join(UPLOAD_FOLDER, file.filename)
    output_pdf = os.path.join(UPLOAD_FOLDER, "highlighted_" + file.filename)

    file.save(input_pdf)
    highlight_large_qty(input_pdf, output_pdf)

    return send_file(output_pdf, as_attachment=True)

# Run Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port
    app.run(host="0.0.0.0", port=port)
