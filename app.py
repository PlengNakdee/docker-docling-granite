import re, html, tempfile, os, json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from docling.document_converter import DocumentConverter
import os as env_os

app = FastAPI()

env_os.environ['DOCLING_MODEL'] = 'ibm-granite/granite-docling-258M'

converter = DocumentConverter()

@app.post('/docling')
async def process_document(request: Request):
    try:
        contents = await request.body()
        header = request.headers
        doc_type = header.get("type")
        file_extension = '.pdf'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name
        
        result = process_with_docling(temp_path)
        os.unlink(temp_path)
        
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
        os.makedirs("/app/output", exist_ok=True)
        
        with open(f"/app/output/docling_{doc_type}.json", 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        
        return response_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


def process_with_docling(file_path):
    try:
        result = converter.convert(file_path)
        extracted_text = result.document.export_to_dict()

        return {
            "extracted_text": extracted_text,
            "total_pages": len(result.document.pages) if hasattr(result.document, 'pages') else 1,
            "extraction_method": "Docling with Granite-258M",
            "metadata": result.metadata if hasattr(result, 'metadata') else {},
            "status": "success"
        }
        
    except Exception as e:
        return {"error": f"Docling processing failed: {str(e)}"}
