# File Metadata Guide - How to Get File Size and Name

## Overview
This guide explains how to get file metadata (file size, name, content type) when adding files through the Django admin panel.

## **Option 1: Automatic File Upload (Recommended)**

### **How It Works:**
The enhanced admin panel now supports actual file uploads and automatically extracts metadata:

1. **Upload File**: Select a file in the admin form
2. **Auto-fill Metadata**: File size, name, and content type are automatically populated
3. **Storage Upload**: File is uploaded to Firebase/local storage
4. **Database Record**: Complete file record is created with all metadata

### **Steps:**
1. **Navigate to**: Files → File uploads → Add file upload
2. **File Upload Section**: 
   - Click "Choose File" and select your transcript/document
   - The file field will appear at the top
3. **Fill Required Fields**:
   - **School**: Select the school this file belongs to
   - **File type**: Choose "transcript" for academic transcripts
   - **Description**: Add a description (optional)
   - **Tags**: Add tags like "academic, transcript, 2024" (optional)
4. **Save**: Click Save - metadata is automatically filled!

### **What Gets Auto-filled:**
- ✅ **Original name**: From uploaded file
- ✅ **File size**: In bytes (automatically calculated)
- ✅ **Content type**: MIME type (e.g., "application/pdf")
- ✅ **Firebase path**: Generated automatically
- ✅ **Firebase URL**: After successful upload

---

## **Option 2: Manual Entry (For Existing Files)**

### **When to Use:**
- Adding records for files already uploaded elsewhere
- Creating placeholder records
- Testing without actual file uploads

### **Required Fields to Fill Manually:**
1. **Original name**: Enter filename (e.g., "student_transcript_2024.pdf")
2. **File size**: Enter size in bytes (e.g., 1048576 for 1MB)
3. **Content type**: Enter MIME type (e.g., "application/pdf")
4. **Firebase path**: Enter storage path
5. **Firebase URL**: Enter public URL to the file

### **File Size Conversion:**
```
1 MB = 1,048,576 bytes
2 MB = 2,097,152 bytes
5 MB = 5,242,880 bytes
10 MB = 10,485,760 bytes
```

### **Common Content Types:**
```
PDF: application/pdf
Word: application/msword
Word (new): application/vnd.openxmlformats-officedocument.wordprocessingml.document
JPEG: image/jpeg
PNG: image/png
Text: text/plain
```

---

## **Option 3: API Endpoints (For Programmatic Uploads)**

### **Use the API for:**
- Bulk file uploads
- Integration with other systems
- Automated file processing

### **API Endpoints:**
```bash
# Upload new file
POST /api/files/upload/

# Test upload
POST /api/files/test_upload/
```

### **API Request Example:**
```bash
curl -X POST /api/files/upload/ \
  -H "Authorization: Bearer {token}" \
  -F "file=@transcript.pdf" \
  -F "file_type=transcript" \
  -F "description=Student transcript for 2024" \
  -F "tags=academic,transcript,2024"
```

---

## **File Metadata Examples**

### **Example 1: PDF Transcript**
```
Original name: student_transcript_2024.pdf
File size: 1048576 (1 MB)
Content type: application/pdf
Firebase path: schools/1/transcript/20241201_abc123.pdf
Firebase URL: https://firebasestorage.googleapis.com/...
```

### **Example 2: Word Document**
```
Original name: behavior_report_jan2024.docx
File size: 2097152 (2 MB)
Content type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Firebase path: schools/1/behavior_report/20241201_def456.docx
Firebase URL: https://firebasestorage.googleapis.com/...
```

### **Example 3: Image File**
```
Original name: student_photo.jpg
File size: 524288 (0.5 MB)
Content type: image/jpeg
Firebase path: schools/1/student_document/20241201_ghi789.jpg
Firebase URL: https://firebasestorage.googleapis.com/...
```

---

## **Troubleshooting**

### **Common Issues:**

1. **"File size required"**
   - Use Option 1 (automatic upload) instead of manual entry
   - Or convert file size to bytes manually

2. **"Content type required"**
   - Use Option 1 for automatic detection
   - Or look up MIME type for your file extension

3. **"Firebase path required"**
   - Use Option 1 for automatic generation
   - Or follow pattern: `schools/{school_id}/{file_type}/{filename}`

4. **"File upload failed"**
   - Check Firebase configuration
   - Ensure file size is under 10MB limit
   - Verify file type is allowed

### **File Size Limits:**
- **Maximum file size**: 10MB
- **Allowed types**: PDF, DOC, DOCX, JPG, PNG, GIF, TXT
- **Storage**: Firebase (if configured) or local storage

---

## **Best Practices**

### **For Transcripts:**
1. **Use Option 1** (automatic upload) when possible
2. **Consistent naming**: `{student_name}_transcript_{year}.pdf`
3. **Descriptive tags**: "academic, transcript, 2024, grade10"
4. **School association**: Always select the correct school

### **For Organization:**
1. **File types**: Use consistent categories (transcript, behavior_report, etc.)
2. **Tags**: Use comma-separated, searchable tags
3. **Descriptions**: Add meaningful descriptions for better searchability
4. **Access control**: Set appropriate public/private status

---

## **Quick Reference**

### **Admin Panel Workflow:**
1. **Files** → **File uploads** → **Add file upload**
2. **Upload file** in File Upload section
3. **Select school** and **file type**
4. **Add description** and **tags**
5. **Save** - metadata auto-filled!

### **Manual Entry Fields:**
- ✅ School (required)
- ✅ File type (required)
- ✅ Original name (required)
- ✅ File size in bytes (required)
- ✅ Content type (required)
- ✅ Firebase path (required)
- ✅ Firebase URL (required)
- ⚪ Description (optional)
- ⚪ Tags (optional)
- ⚪ Public status (optional)

---

**Note**: The enhanced admin panel now supports both automatic file uploads (recommended) and manual entry. Use automatic uploads for new files to avoid manual metadata entry errors.
