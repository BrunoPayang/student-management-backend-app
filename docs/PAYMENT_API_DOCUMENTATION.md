# Payment System API Documentation

**Version:** 1.0  
**Last Updated:** January 2024  
**For:** Frontend Dashboard Development Team

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Data Models](#data-models)
4. [API Endpoints](#api-endpoints)
5. [Common Use Cases](#common-use-cases)
6. [Error Handling](#error-handling)
7. [Example Requests](#example-requests)
8. [Frontend Integration Tips](#frontend-integration-tips)

---

## 🏗️ Overview

The Payment System manages student fee records, payment tracking, and financial reporting for schools. It provides comprehensive APIs for creating, updating, and monitoring payment records.

### Key Features
- ✅ Multi-type fee management (tuition, library, sports, etc.)
- ✅ Payment status tracking (pending → paid/overdue/cancelled)
- ✅ Multiple payment methods support
- ✅ Overdue payment detection
- ✅ Financial reporting and statistics
- ✅ School-based data isolation
- ✅ Receipt URL management

---

## 🔐 Authentication

All payment endpoints require JWT authentication:

```http
Authorization: Bearer your_jwt_token_here
```

**Getting Token:**
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@school.com",
    "password": "password"
}
```

---

## 📊 Data Models

### PaymentRecord Model

| Field | Type | Required | Description | Choices/Format |
|-------|------|----------|-------------|----------------|
| `id` | Integer | Auto | Primary key | Read-only |
| `student` | Integer | Yes | Student ID (Foreign Key) | Must be valid student ID |
| `amount` | Decimal | Yes | Payment amount | Max 10 digits, 2 decimal places |
| `currency` | String | No | Currency code | Default: "NGN", Max 3 chars |
| `payment_type` | String | Yes | Type of fee | See [Payment Types](#payment-types) |
| `status` | String | No | Payment status | Default: "pending", See [Status Options](#status-options) |
| `due_date` | Date | Yes | Payment due date | Format: "YYYY-MM-DD" |
| `paid_date` | Date | No | Date when paid | Format: "YYYY-MM-DD" |
| `payment_method` | String | No | How payment was made | See [Payment Methods](#payment-methods) |
| `reference_number` | String | No | Transaction reference | Max 100 chars |
| `receipt_url` | URL | No | Link to receipt | Valid URL |
| `notes` | Text | No | Additional notes | Unlimited text |
| `created_by` | Integer | Auto | User who created record | Read-only |
| `created_at` | DateTime | Auto | Creation timestamp | Read-only |
| `updated_at` | DateTime | Auto | Last update timestamp | Read-only |

#### Payment Types
```javascript
const PAYMENT_TYPES = {
    'tuition': 'Tuition Fee',
    'library': 'Library Fee', 
    'laboratory': 'Laboratory Fee',
    'sports': 'Sports Fee',
    'transport': 'Transport Fee',
    'meal': 'Meal Fee',
    'uniform': 'Uniform Fee',
    'examination': 'Examination Fee',
    'other': 'Other'
};
```

#### Status Options
```javascript
const PAYMENT_STATUS = {
    'pending': 'Pending',
    'paid': 'Paid',
    'overdue': 'Overdue', 
    'cancelled': 'Cancelled',
    'refunded': 'Refunded'
};
```

#### Payment Methods
```javascript
const PAYMENT_METHODS = {
    'cash': 'Cash',
    'bank_transfer': 'Bank Transfer',
    'card': 'Credit/Debit Card',
    'mobile_money': 'Mobile Money',
    'check': 'Check',
    'other': 'Other'
};
```

### Computed Fields (Read-Only)

| Field | Type | Description |
|-------|------|-------------|
| `student_name` | String | Full name of the student |
| `created_by_name` | String | Full name of user who created record |
| `days_overdue` | Integer | Number of days payment is overdue (0 if not overdue) |

---

## 🚀 API Endpoints

### Base URL
```
http://your-domain.com/api
```

### 1. Payment Records Management

#### 📋 List All Payment Records
```http
GET /api/payment-records/
```

**Query Parameters:**
- `payment_type`: Filter by payment type
- `status`: Filter by status
- `currency`: Filter by currency
- `search`: Search by student name or reference number
- `page`: Page number for pagination
- `page_size`: Number of records per page

**Response:**
```json
{
    "count": 150,
    "next": "http://api/payment-records/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "student": 1,
            "student_name": "John Doe",
            "amount": "50000.00",
            "currency": "NGN",
            "payment_type": "tuition",
            "status": "pending",
            "due_date": "2024-03-31",
            "paid_date": null,
            "payment_method": "",
            "reference_number": "",
            "receipt_url": null,
            "notes": "Q1 2024 tuition fee",
            "created_by": 1,
            "created_by_name": "Admin User",
            "days_overdue": 0,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### 📝 Create Payment Record
```http
POST /api/payment-records/
Content-Type: application/json
```

**Request Body:**
```json
{
    "student": "ce695f13-acef-4dac-8c21-b83a2c37d204",
    "amount": "75000.00",
    "currency": "NGN",
    "payment_type": "tuition",
    "status": "pending",
    "due_date": "2024-03-31",
    "notes": "Q1 2024 tuition fee"
}
```

**Note:** The `student` field expects a **UUID string** (not integer). Get valid student UUIDs from the `/api/students/` endpoint.

**Response:** Same as individual record above

#### 👁️ Get Specific Payment Record
```http
GET /api/payment-records/{payment_id}/
```

#### ✏️ Update Payment Record (Partial)
```http
PATCH /api/payment-records/{payment_id}/
Content-Type: application/json
```

**Common Update Examples:**

**Mark as Paid:**
```json
{
    "status": "paid",
    "paid_date": "2024-01-20",
    "payment_method": "bank_transfer",
    "reference_number": "TXN123456789"
}
```

**Mark as Overdue:**
```json
{
    "status": "overdue"
}
```

#### 🔄 Replace Payment Record (Full Update)
```http
PUT /api/payment-records/{payment_id}/
Content-Type: application/json
```

#### 🗑️ Delete Payment Record
```http
DELETE /api/payment-records/{payment_id}/
```

### 2. Special Payment Endpoints

#### ⚠️ Get Overdue Payments
```http
GET /api/payment-records/overdue_payments/
```

**Response:**
```json
[
    {
        "id": 5,
        "student_name": "Jane Smith",
        "amount": "25000.00",
        "payment_type": "library",
        "due_date": "2024-01-15",
        "days_overdue": 10,
        // ... other fields
    }
]
```

#### 📈 Get Payment Summary Statistics
```http
GET /api/payment-records/payment_summary/
```

**Response:**
```json
{
    "total_payments": 245,
    "total_amount": 12450000.00,
    "paid_amount": 8500000.00,
    "pending_amount": 3200000.00,
    "overdue_amount": 750000.00,
    "payment_types": [
        {
            "payment_type": "tuition",
            "count": 120,
            "total_amount": 6000000.00
        },
        {
            "payment_type": "library", 
            "count": 45,
            "total_amount": 225000.00
        }
    ]
}
```

### 3. Student-Specific Payment Endpoints

#### 📚 Get Student's Payment Records
```http
GET /api/students/{student_id}/payment_records/
```

**Response:**
```json
[
    {
        "id": 1,
        "amount": "50000.00",
        "payment_type": "tuition",
        "status": "paid",
        // ... other payment fields
    }
]
```

#### 📊 Get Student Complete Statistics
```http
GET /api/students/{student_id}/statistics/
```

**Response:**
```json
{
    "academic": {
        "total_transcripts": 3,
        "average_gpa": 3.4
    },
    "behavior": {
        "positive_reports": 5,
        "negative_reports": 1,
        "total_reports": 6
    },
    "payments": {
        "total_payments": 8,
        "paid_payments": 6,
        "overdue_payments": 1,
        "total_amount": 400000.00
    }
}
```

---

## 🎯 Common Use Cases

### 1. School Dashboard - Payment Overview

**Get Payment Summary for Dashboard:**
```javascript
// Get overall payment statistics
const response = await fetch('/api/payment-records/payment_summary/', {
    headers: { 'Authorization': `Bearer ${token}` }
});
const summary = await response.json();

// Display cards showing:
// - Total Revenue: summary.paid_amount
// - Pending Amount: summary.pending_amount  
// - Overdue Amount: summary.overdue_amount
// - Total Students with Payments: summary.total_payments
```

### 2. Overdue Payments Alert

**Get Overdue Payments for Alert System:**
```javascript
const response = await fetch('/api/payment-records/overdue_payments/', {
    headers: { 'Authorization': `Bearer ${token}` }
});
const overduePayments = await response.json();

// Show notification badge with count
// List overdue payments with student names and amounts
```

### 3. Create Fee Record for New Term

**Bulk Create Tuition Fees:**
```javascript
const students = await getStudents(); // Your method to get students

for (const student of students) {
    await fetch('/api/payment-records/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            student: student.id,
            amount: "100000.00",
            payment_type: "tuition",
            due_date: "2024-03-31",
            notes: "Q1 2024 tuition fee"
        })
    });
}
```

### 4. Process Payment

**Mark Payment as Paid:**
```javascript
const markAsPaid = async (paymentId, paymentDetails) => {
    const response = await fetch(`/api/payment-records/${paymentId}/`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: 'paid',
            paid_date: new Date().toISOString().split('T')[0], // Today's date
            payment_method: paymentDetails.method,
            reference_number: paymentDetails.reference,
            receipt_url: paymentDetails.receiptUrl
        })
    });
    return response.json();
};
```

### 5. Student Profile - Payment History

**Load Student Payment History:**
```javascript
const loadStudentPayments = async (studentId) => {
    const response = await fetch(`/api/students/${studentId}/payment_records/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
};
```

### 6. Filter and Search Payments

**Advanced Filtering:**
```javascript
const filterPayments = async (filters) => {
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status', filters.status);
    if (filters.paymentType) params.append('payment_type', filters.paymentType);
    if (filters.search) params.append('search', filters.search);
    
    const response = await fetch(`/api/payment-records/?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
};

// Usage examples:
// filterPayments({ status: 'pending' })
// filterPayments({ paymentType: 'tuition', status: 'overdue' })
// filterPayments({ search: 'John Doe' })
```

---

## ❌ Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid data sent |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | No permission for this resource |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal server error |

### Error Response Format

```json
{
    "error": "Validation failed",
    "details": {
        "amount": ["This field is required."],
        "due_date": ["Date format should be YYYY-MM-DD."]
    }
}
```

### Common Validation Errors

```javascript
// Handle validation errors
const handleErrors = (response) => {
    if (!response.ok) {
        if (response.status === 400) {
            // Show field-specific errors
            response.json().then(errorData => {
                Object.keys(errorData.details).forEach(field => {
                    showFieldError(field, errorData.details[field][0]);
                });
            });
        } else if (response.status === 401) {
            // Redirect to login
            redirectToLogin();
        }
    }
};
```

---

## 📋 Example Requests

### Complete Payment Workflow

```javascript
// 1. Create a new payment record
const createPayment = async () => {
    const response = await fetch('/api/payment-records/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            student: 1,
            amount: "50000.00",
            currency: "NGN",
            payment_type: "tuition",
            status: "pending",
            due_date: "2024-03-31",
            notes: "Q1 2024 tuition fee"
        })
    });
    
    if (response.ok) {
        const payment = await response.json();
        console.log('Payment created:', payment.id);
        return payment;
    }
};

// 2. Mark payment as paid
const processPayment = async (paymentId) => {
    const response = await fetch(`/api/payment-records/${paymentId}/`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: 'paid',
            paid_date: '2024-01-20',
            payment_method: 'bank_transfer',
            reference_number: 'TXN123456789'
        })
    });
    
    if (response.ok) {
        const updatedPayment = await response.json();
        console.log('Payment processed:', updatedPayment);
        return updatedPayment;
    }
};

// 3. Get payment statistics for dashboard
const getDashboardStats = async () => {
    const response = await fetch('/api/payment-records/payment_summary/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
        const stats = await response.json();
        updateDashboard(stats);
    }
};
```

---

## 💡 Frontend Integration Tips

### 1. State Management

```javascript
// Example using React/Redux or similar
const paymentSlice = {
    // State
    payments: [],
    overdue: [],
    summary: {},
    loading: false,
    
    // Actions
    fetchPayments: async (filters = {}) => {
        // Implementation
    },
    createPayment: async (paymentData) => {
        // Implementation  
    },
    updatePayment: async (id, updateData) => {
        // Implementation
    }
};
```

### 2. Real-time Updates

```javascript
// Refresh data after operations
const refreshPaymentData = async () => {
    await Promise.all([
        fetchPayments(),
        fetchOverduePayments(), 
        fetchPaymentSummary()
    ]);
};

// Call after create/update operations
await createPayment(data);
await refreshPaymentData();
```

### 3. Data Formatting

```javascript
// Format currency for display
const formatCurrency = (amount, currency = 'NGN') => {
    return new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: currency
    }).format(amount);
};

// Format dates
const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-NG');
};

// Payment type display
const getPaymentTypeLabel = (type) => {
    const labels = {
        'tuition': 'Tuition Fee',
        'library': 'Library Fee',
        // ... other mappings
    };
    return labels[type] || type;
};
```

### 4. Pagination Handling

```javascript
const loadMorePayments = async (nextUrl) => {
    if (nextUrl) {
        const response = await fetch(nextUrl, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        // Append to existing payments
        setPayments(prev => [...prev, ...data.results]);
        setNextUrl(data.next);
    }
};
```

### 5. Dashboard Components Suggestions

#### Payment Summary Cards
```jsx
<div className="payment-summary">
    <Card title="Total Revenue" value={formatCurrency(summary.paid_amount)} />
    <Card title="Pending" value={formatCurrency(summary.pending_amount)} />
    <Card title="Overdue" value={formatCurrency(summary.overdue_amount)} />
    <Card title="Total Payments" value={summary.total_payments} />
</div>
```

#### Overdue Payments Alert
```jsx
<Alert type="warning" visible={overduePayments.length > 0}>
    {overduePayments.length} payments are overdue
    <Button onClick={() => showOverdueList()}>View Details</Button>
</Alert>
```

#### Payment Filters
```jsx
<FilterPanel>
    <Select name="status" options={PAYMENT_STATUS} />
    <Select name="payment_type" options={PAYMENT_TYPES} />
    <SearchInput name="search" placeholder="Search student or reference..." />
</FilterPanel>
```

---

## 🚀 Getting Started Checklist

- [ ] Set up authentication with JWT tokens
- [ ] Test API endpoints with sample data
- [ ] Implement payment summary dashboard
- [ ] Create payment creation form
- [ ] Add payment history views
- [ ] Implement overdue payment alerts
- [ ] Set up real-time data refresh
- [ ] Add proper error handling
- [ ] Test all CRUD operations
- [ ] Implement filtering and search

---

## 📞 Support

For questions about this API documentation:
- Backend Team: backend@school.com
- API Issues: Create issue in project repository
- Emergency: Contact system administrator

**Last Updated:** January 2024  
**API Version:** v1.0
