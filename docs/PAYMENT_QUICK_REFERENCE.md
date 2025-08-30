# Payment API Quick Reference Guide

**For Frontend Developers** | **School Dashboard Integration**

## 🎯 Essential Endpoints

### Dashboard Overview
```javascript
// Get payment statistics for dashboard cards
GET /api/payment-records/payment_summary/
// Returns: total_amount, paid_amount, pending_amount, overdue_amount

// Get overdue payments count for alerts  
GET /api/payment-records/overdue_payments/
// Returns: Array of overdue payment records
```

### Payment Management
```javascript
// List all payments (with filters)
GET /api/payment-records/?status=pending&payment_type=tuition

// Create new payment record
POST /api/payment-records/
Body: { student: 1, amount: "50000.00", payment_type: "tuition", due_date: "2024-03-31" }

// Mark payment as paid
PATCH /api/payment-records/{id}/
Body: { status: "paid", paid_date: "2024-01-20", payment_method: "bank_transfer" }
```

### Student-Specific
```javascript
// Get all payments for a student
GET /api/students/{student_id}/payment_records/

// Get student stats (includes payment summary)
GET /api/students/{student_id}/statistics/
```

## 📊 Data Structures

### Payment Record
```javascript
{
    "id": 1,
    "student": 1,
    "student_name": "John Doe",           // Read-only
    "amount": "50000.00",
    "currency": "NGN",
    "payment_type": "tuition",            // tuition|library|sports|etc
    "status": "pending",                  // pending|paid|overdue|cancelled|refunded
    "due_date": "2024-03-31",
    "paid_date": null,
    "payment_method": "",                 // cash|bank_transfer|card|mobile_money|etc
    "reference_number": "",
    "receipt_url": null,
    "notes": "",
    "created_by_name": "Admin User",      // Read-only
    "days_overdue": 0,                    // Read-only
    "created_at": "2024-01-15T10:30:00Z"  // Read-only
}
```

### Payment Summary
```javascript
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
        }
    ]
}
```

## 🎨 UI Components Suggestions

### Dashboard Cards
```jsx
// Payment summary cards
<Card title="Total Revenue" value={formatCurrency(summary.paid_amount)} color="green" />
<Card title="Pending Payments" value={formatCurrency(summary.pending_amount)} color="blue" />
<Card title="Overdue Payments" value={formatCurrency(summary.overdue_amount)} color="red" />
```

### Payment Status Badge
```jsx
const StatusBadge = ({ status }) => {
    const colors = {
        pending: 'yellow',
        paid: 'green', 
        overdue: 'red',
        cancelled: 'gray',
        refunded: 'purple'
    };
    return <Badge color={colors[status]}>{status}</Badge>;
};
```

### Payment Type Icon
```jsx
const PaymentTypeIcon = ({ type }) => {
    const icons = {
        tuition: '🎓',
        library: '📚',
        sports: '⚽',
        transport: '🚌',
        meal: '🍽️',
        uniform: '👕',
        laboratory: '🔬',
        examination: '📝'
    };
    return <span>{icons[type] || '💰'}</span>;
};
```

## 🔍 Common Filters

```javascript
// Status filter
const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'pending', label: 'Pending' },
    { value: 'paid', label: 'Paid' },
    { value: 'overdue', label: 'Overdue' },
    { value: 'cancelled', label: 'Cancelled' }
];

// Payment type filter  
const typeOptions = [
    { value: '', label: 'All Types' },
    { value: 'tuition', label: 'Tuition Fee' },
    { value: 'library', label: 'Library Fee' },
    { value: 'sports', label: 'Sports Fee' }
];
```

## ⚡ Quick Actions

### Mark Multiple Payments as Paid
```javascript
const markMultipleAsPaid = async (paymentIds, paymentDetails) => {
    const promises = paymentIds.map(id => 
        fetch(`/api/payment-records/${id}/`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: 'paid',
                paid_date: new Date().toISOString().split('T')[0],
                ...paymentDetails
            })
        })
    );
    
    await Promise.all(promises);
    refreshPaymentData();
};
```

### Create Bulk Payments for All Students
```javascript
const createBulkPayments = async (paymentData) => {
    const students = await fetchStudents();
    
    const promises = students.map(student =>
        fetch('/api/payment-records/', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student: student.id,
                ...paymentData
            })
        })
    );
    
    await Promise.all(promises);
};
```

## 🔄 Real-time Updates

```javascript
// Refresh dashboard data every 30 seconds
useEffect(() => {
    const interval = setInterval(async () => {
        const summary = await fetchPaymentSummary();
        const overdue = await fetchOverduePayments();
        updateDashboard({ summary, overdue });
    }, 30000);
    
    return () => clearInterval(interval);
}, []);
```

## 🎯 Error Handling

```javascript
const handleApiError = (response) => {
    if (response.status === 401) {
        // Token expired
        redirectToLogin();
    } else if (response.status === 400) {
        // Validation error
        response.json().then(data => {
            showToast('Please check your input', 'error');
        });
    } else {
        showToast('Something went wrong', 'error');
    }
};
```

## 💡 Performance Tips

1. **Pagination**: Use `page_size=50` for better performance
2. **Caching**: Cache payment summary for 5 minutes
3. **Lazy Loading**: Load payment details on demand
4. **Debounced Search**: Wait 300ms after user stops typing

## 📱 Mobile Considerations

- Use collapsible payment cards on small screens
- Implement swipe actions for quick status updates
- Show essential info only (amount, type, status, due date)
- Use bottom sheet for payment details

---

**Need help?** Check the full documentation: `PAYMENT_API_DOCUMENTATION.md`

