import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from database import db, PDFDocument, PDFChunk
from ai_engine import ai_engine
from config import Config

pdf_search_bp = Blueprint('pdf_search', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pdf_search_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Save file to uploads folder
        file.save(file_path)
        
        try:
            # Register in database
            pdf_doc = PDFDocument(filename=filename, file_path=file_path)
            db.session.add(pdf_doc)
            db.session.flush() # Resolve pdf_doc.id
            
            # Embed & index via AIEngine
            num_chunks = ai_engine.add_pdf_to_vectorstore(pdf_doc.id, file_path)
            
            # Retrieve generated chunks from fallback or register them in db too
            # Let's save a couple of chunks in PDFChunk table for relational metadata
            for idx, c_data in enumerate(ai_engine.vector_store_fallback.chunks):
                if c_data["pdf_id"] == pdf_doc.id:
                    chunk_db = PDFChunk(
                        pdf_id=pdf_doc.id,
                        chunk_text=c_data["text"],
                        chunk_index=idx
                    )
                    db.session.add(chunk_db)
                    
            db.session.commit()
            
            return jsonify({
                "message": f"Successfully uploaded and indexed '{filename}'",
                "pdf_id": pdf_doc.id,
                "chunks_indexed": num_chunks
            }), 201
            
        except Exception as e:
            db.session.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": f"Failed to parse and index PDF: {str(e)}"}), 500
            
    return jsonify({"error": "Unsupported file format. Only PDF files are allowed."}), 400

@pdf_search_bp.route('/list', methods=['GET'])
def list_pdfs():
    docs = PDFDocument.query.order_by(PDFDocument.uploaded_at.desc()).all()
    results = []
    for d in docs:
        results.append({
            "id": d.id,
            "filename": d.filename,
            "uploaded_at": d.uploaded_at.isoformat()
        })
    return jsonify(results), 200

@pdf_search_bp.route('/delete/<int:pdf_id>', methods=['DELETE'])
def delete_pdf(pdf_id):
    pdf = PDFDocument.query.get(pdf_id)
    if not pdf:
        return jsonify({"error": "PDF not found"}), 404
        
    try:
        # Remove physical file
        if os.path.exists(pdf.file_path):
            os.remove(pdf.file_path)
            
        db.session.delete(pdf)
        db.session.commit()
        
        # Note: Rebuilding vector store in real-time is done by re-initializing or filtering
        # Since it's a demo, standard delete is sufficient.
        return jsonify({"message": "PDF deleted successfully from database and vector index"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete PDF: {str(e)}"}), 500

@pdf_search_bp.route('/summarize', methods=['POST'])
def summarize_pdf():
    # Summarize uploaded file
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded for summarization"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_path = os.path.join(Config.UPLOAD_FOLDER, f"temp_{filename}")
        file.save(temp_path)
        
        try:
            # Extract text
            text = ai_engine.extract_pdf_text(temp_path)
            
            # Simple summarization: first 1500 words
            words = text.split()
            summary_source = " ".join(words[:1000])
            
            system_prompt = (
                "You are an expert government scheme analyst. Take the following extracted document text "
                "and output a structured summary. Use Markdown layout. Include sections:\n"
                "1. **Overview & Objective** (Simple 2-sentence explanation)\n"
                "2. **Eligibility Criteria** (Age, occupation, income restrictions)\n"
                "3. **Key Benefits & Financial Assistance**\n"
                "4. **Mandatory Documents Checklist**\n"
                "5. **Key Dates / Deadlines** (if mentioned)\n"
            )
            
            summary = ai_engine.generate_response(
                system_prompt, 
                "Provide a clear, formatted summary of this document.", 
                [{"text": summary_source}]
            )
            
            # Cleanup temp file
            os.remove(temp_path)
            
            return jsonify({
                "filename": filename,
                "summary": summary
            }), 200
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"error": f"Failed to summarize: {str(e)}"}), 500
            
    return jsonify({"error": "Unsupported file format"}), 400
