# Django 5.0+ Test Fixes Guide

## Problem Summary

Tests are failing due to Django 5.0+ backwards incompatible changes:

1. **Unsaved model instances cannot be assigned to ForeignKey fields**
2. **Mock decorators referencing class attributes set in `setUpTestData()` fail because the decorator is evaluated at class definition time when the attribute is `None`**

## Error Messages You'll See

```
ValueError: "<Report: Report object (None)>" needs to have a value for field "id" before this relationship can be used.
```

```
ValueError: Cannot determine the current user for report disposal.
```

## Fix #1: crt_portal/cts_forms/tests/test_models.py

### Changes Needed:

**Line 206:** Change from:
```python
test_user = User(username='disposition_test_user')
```

**To:**
```python
test_user = None
```

**Lines 210-211:** Change from:
```python
User.objects.filter(username='disposition_test_user').delete()
cls.test_user.save()
```

**To:**
```python
User.objects.filter(username='disposition_test_user').delete()
# Django 5.0+: Create and save User instance in setUpTestData
cls.test_user = User.objects.create(username='disposition_test_user')
```

**Lines 224-242:** Replace the entire `test_disposition` method from:
```python
@mock.patch('crequest.middleware.CrequestMiddleware.get_request',
            return_value=mock.Mock(user=test_user))
def test_disposition(self, mock_crequest_middleware: mock.Mock):
    reports = Report.objects.filter(location_name='batch disposition tests')
    batch = ReportDispositionBatch.dispose(reports)
    self.assertEqual(batch.disposed_by.get_username(), 'disposition_test_user')
    self.assertEqual(batch.disposed_count, 3)
    self.assertEqual(batch.disposed_reports.count(), 3)
    self.assertEqual({
        disposed.schedule.name
        for disposed in batch.disposed_reports.all()
    }, {'1 Year', '3 Year