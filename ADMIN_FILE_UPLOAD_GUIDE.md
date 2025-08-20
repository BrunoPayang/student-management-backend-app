# Django Admin Panel - File Upload Guide for Super Admin

## Overview
This guide explains how super admin users can upload and manage files (including transcripts) through the Django admin panel.

## Accessing the Admin Panel

### 1. **Login to Admin Panel**
- Navigate to: `http://localhost:8000/admin/` (or your domain)
- Use your superuser credentials to log in

### 2. **Available Sections**
After logging in, you'll see:
- **Files** → **File uploads** - Manage all file uploads
- **Schools** → **Schools** - Manage school information  
- **Authentication and authorization** → **Users** - Manage user accounts

## Adding Files via Admin Panel

### **Step 1: Navigate to File Uploads**
1. Click on **Files** in the admin panel
2. Click on **File uploads**
3. Click **Add file upload** button

### **Step 2: Fill in File Information**

#### **File Information Section:**
- **Original name**: Enter the filename (e.g., "student_transcript_2024.pdf")
- **File type**: Select from dropdown:
  - `transcript` - Academic Transcript
  - `behavior_report` - Behavior Report
  - `payment_receipt` - Payment Receipt
  - `student_document` - Student Document
  - `other` - Other documents
- **Description**: Optional description of the file
- **Tags**: Optional comma-separated tags (e.g., "academic, transcript, 2024")

#### **Storage Details Section:**
- **Firebase path**: Enter the storage path (e.g., "schools/1/transcript/20241201_abc123.pdf")
- **Firebase URL**: Enter the public URL to the file
- **File size**: Enter file size in bytes
- **Content type**: Enter MIME type (e.g., "application/pdf")

#### **School & Access Section:**
- **School**: Select the school this file belongs to
- **Is public**: Checkbox to make file publicly accessible
- **Is deleted**: Checkbox to mark file as deleted (soft delete)

#### **Upload Details Section:**
- **Uploaded by**: Automatically set to current user
- **Uploaded at**: Automatically set to current timestamp

### **Step 3: Save the File**
Click **Save** to create the file record.

## Managing Existing Files

### **File List View**
The admin panel shows:
- File ID
- Original filename
- File type
- School
- Uploaded by user
- File size (in MB)
- Upload date
- Public status
- Deleted status

### **Filtering and Search**
- **Filters**: Filter by file type, school, public status, deleted status, upload date
- **Search**: Search by filename, description, tags, school name, or uploader

### **Bulk Operations**
Select multiple files and use these actions:
- **Mark selected files as public** - Make files publicly accessible
- **Mark selected files as private** - Make files private
- **Mark selected files as deleted** - Soft delete files
- **Mark selected files as active** - Restore deleted files

## File Upload Workflow

### **For Transcripts:**
1. **Upload file to storage first** (Firebase or local)
2. **Get storage details**:
   - Firebase path
   - Firebase URL
   - File size
   - Content type
3. **Add file record in admin**:
   - Set file type to "transcript"
   - Associate with appropriate school
   - Add descriptive metadata
4. **Set access permissions**:
   - Public/private status
   - School association

### **Example Transcript Entry:**
```
File Information:
- Original name: student_transcript_2024.pdf
- File type: transcript
- Description: Student academic transcript for 2024
- Tags: academic, transcript, 2024

Storage Details:
- Firebase path: schools/1/transcript/20241201_student123.pdf
- Firebase URL: https://firebasestorage.googleapis.com/...
- File size: 1048576
- Content type: application/pdf

School & Access:
- School: ABC High School
- Is public: No
- Is deleted: No
```

## Admin Panel Features

### **Super Admin Privileges:**
- ✅ **View all files** across all schools
- ✅ **Add files** for any school
- ✅ **Edit file metadata** (description, tags, public status)
- ✅ **Delete files** (soft delete)
- ✅ **Bulk operations** on multiple files
- ✅ **Advanced filtering** and search

### **Security Features:**
- **Permission-based access**: Only super admins can access admin panel
- **Audit trail**: All changes are logged
- **School isolation**: Files are properly scoped to schools
- **Soft delete**: Files are marked deleted but not physically removed

## Troubleshooting

### **Common Issues:**

1. **"No files showing"**
   - Check if schools exist in database
   - Run: `python manage.py seed_schools`
   - Verify file uploads exist

2. **"Permission denied"**
   - Ensure you're logged in as superuser
   - Check user permissions in Django admin

3. **"School field required"**
   - Create schools first using seed command
   - Ensure schools exist before adding files

### **Useful Commands:**
```bash
# Create superuser (if none exists)
python manage.py createsuperuser

# Seed schools data
python manage.py seed_schools

# Check file count
python manage.py shell -c "from apps.files.models import FileUpload; print(f'Total files: {FileUpload.objects.count()}')"

# Check school count
python manage.py shell -c "from apps.schools.models import School; print(f'Total schools: {School.objects.count()}')"
```

## Best Practices

1. **File Organization**: Use consistent naming conventions
2. **Metadata**: Always add descriptions and tags for better searchability
3. **Access Control**: Be careful with public/private settings
4. **Regular Maintenance**: Periodically review and clean up old files
5. **Backup**: Ensure file storage is properly backed up

## Support

If you encounter issues:
1. Check the Django admin logs
2. Verify database connectivity
3. Ensure all migrations are applied
4. Check file storage configuration (Firebase/local)

---

**Note**: This admin panel is designed for super admin users only. School staff and parents should use the API endpoints for file operations.
