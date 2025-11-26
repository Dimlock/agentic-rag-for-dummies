import os

from docling.datamodel.base_models import InputFormat

import config
import pymupdf.layout
import pymupdf4llm
from pathlib import Path
import glob
from docling.document_converter import DocumentConverter, PDF, WordFormatOption
from docling.datamodel.pipeline_options import smolvlm_picture_description, PdfPipelineOptions

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def pdf_to_markdown(pdf_path, output_dir):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_picture_description = True
    pipeline_options.picture_description_options = (
        smolvlm_picture_description
    )
    pipeline_options.picture_description_options.prompt = (
        "Опиши картинку в трех предложениях. Будь кратким и точным."
    )
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_picture_images = True
    source = pdf_path  # file path or URL
    converter = DocumentConverter(
        format_options={
            InputFormat.DOCX: WordFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )
    doc = converter.convert(source).document
    md = doc.export_to_markdown()
    md_cleaned = md.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='ignore')
    output_path = Path(output_dir) / Path(doc.name).stem
    Path(output_path).with_suffix(".md").write_bytes(md_cleaned.encode('utf-8'))

def pdfs_to_markdowns(path_pattern, overwrite: bool = False):
    output_dir = Path(config.MARKDOWN_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in map(Path, glob.glob(path_pattern)):
        md_path = (output_dir / pdf_path.stem).with_suffix(".md")
        if overwrite or not md_path.exists():
            pdf_to_markdown(pdf_path, output_dir)