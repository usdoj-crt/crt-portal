# Django 5.0+ Foreign Key Validation Issues

## Issue Summary

Django 5.0 removed support for passing unsaved model instances to related filters and foreign key assignments. This was deprecated in Django 4.1 and fully removed in Django 5.0.

## Source Documentation

**Django 4.1 Release Notes - Features deprecated in 4.1:**
https://docs.djangoproject.com/en/4.1/releases/4.1/#miscellaneous

> "Passing unsaved model instances to related filters is deprecated. In Django 5.0, the exception will be raised."

**Django 5.0 Release Notes - Features removed in 5.0:**
https://docs.djangoproject.com/en/5.0/releases/5.0/#features-removed-in-5-0

> "Passing unsaved model instances to related filters is no longer allowed."

**Django 4.1 Release Notes - Backwards incompatible changes:**
https://docs.djangoproject.com/en/4.1/releases/4.1/#reverse-foreign-key-changes-for-unsaved-model-instances

> "In order to unify the behavior with many-to-many relations for unsaved model instances, a reverse foreign key now raises `ValueError` when calling related managers for unsaved objects."

## Files with Issues Found

### 1. `crt_portal/utils/tests/test_pdf.py`

**Lines 25-35 (test_tms_converts method):**
```python
report = Report(**SAMPLE_REPORT_1)
report.id = 123
email = TMSEmail(tms_id=456,
                 report=report,  # ❌ UNSAVED REPORT INSTANCE
                 subject='Foo subject',
                 body='Foo body',
                 html_body='<ul><li>Foo body</li></ul>',
                 recipient='foo@example.com',
                 created_at=datetime.datetime.now(),
                 completed_at=datetime.datetime.now(),
                 status=TMSEmail.SENT,
                 purpose=TMSEmail.MANUAL_EMAIL,
                 error_message='oh no bad thing')
```

**Lines 58-68 (test_tms_converts_multiple_recipients method):**
```python
report = Report(**SAMPLE_REPORT_1)
report.public_id = 123
email = TMSEmail(tms_id=456,
                 report=report,  # ❌ UNSAVED REPORT INSTANCE
                 subject='Foo subject',
                 body='Foo body',
                 html_body='<ul><li>Foo body</li></ul>',
                 recipient=['foo@example.com', 'bar@example.com'],
                 created_at=datetime.datetime.now(),
                 completed_at=datetime.datetime.now(),
                 status=TMSEmail.SENT,
                 purpose=TMSEmail.MANUAL_EMAIL,
                 error_message='oh no bad thing')
```

**Problem:** The `Report` instance is created but never saved. Setting `report.id` or `report.public_id` manually does NOT save the instance to the database. When this unsaved instance is assigned to `email.report`, Django 5.0+ will raise a `ValueError`.

### 2. `crt_portal/cts_forms/tests/test_models.py`

**Lines 205-220 (ReportTests class setup):**
```python
class ReportTests(TestCase):
    test_user = User(username='disposition_test_user')  # ❌ UNSAVED USER INSTANCE

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        cls.test_user.save()  # ✅ SAVED LATER, but risky pattern
        test_data = {
            **SAMPLE_REPORT_1.copy(),
            'retention_schedule': RetentionSchedule.objects.get(name='1 Year'),
            'location_name': 'batch disposition tests',
        }
        # ... rest of setup
```

**Problem:** While `test_user` is eventually saved in `setUpTestData()`, declaring it as an unsaved class attribute is a problematic pattern. If any code tries to use `cls.test_user` before `setUpTestData()` runs, it will fail in Django 5.0+.

## How to Fix These Issues

### Fix #1: Save Report instances before assigning to ForeignKey

**File: `crt_portal/utils/tests/test_pdf.py`**

**OLD CODE (Lines 25-27):**
```python
report = Report(**SAMPLE_REPORT_1)
report.id = 123
email = TMSEmail(tms_id=456, report=report, ...)
```

**NEW CODE:**
```python
report = Report.objects.create(**SAMPLE_REPORT_1)
# If you need a specific ID, you can set it, but you must save first
email = TMSEmail(tms_id=456, report=report, ...)
```

**OR if you really need to avoid database operations (for unit tests):**
```python
report = Report(**SAMPLE_REPORT_1)
report.save()  # Must save before assigning to ForeignKey
email = TMSEmail(tms_id=456, report=report, ...)
```

### Fix #2: Don't declare unsaved model instances as class attributes

**File: `crt_portal/cts_forms/tests/test_models.py`**

**OLD CODE:**
```python
class ReportTests(TestCase):
    test_user = User(username='disposition_test_user')  # ❌ Unsaved

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        cls.test_user.save()
```

**NEW CODE:**
```python
class ReportTests(TestCase):
    test_user = None  # Initialize as None

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        cls.test_user = User(username='disposition_test_user')
        cls.test_user.save()
```

**OR better yet:**
```python
class ReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        cls.test_user = User.objects.create(username='disposition_test_user')
```

## Complete Fix for test_pdf.py

```python
def test_tms_converts(self):
    self.maxDiff = 9999999999
    # FIX: Save the report instance before assigning to ForeignKey
    report = Report.objects.create(**SAMPLE_REPORT_1)
    
    email = TMSEmail(tms_id=456,
                     report=report,
                     subject='Foo subject',
                     body='Foo body',
                     html_body='<ul><li>Foo body</li></ul>',
                     recipient='foo@example.com',
                     created_at=datetime.datetime.now(),
                     completed_at=datetime.datetime.now(),
                     status=TMSEmail.SENT,
                     purpose=TMSEmail.MANUAL_EMAIL,
                     error_message='oh no bad thing')

    converted = pdf.convert_tms_to_pdf(email)
    # ... rest of test

def test_tms_converts_multiple_recipients(self):
    self.maxDiff = 9999999999
    # FIX: Save the report instance before assigning to ForeignKey
    report = Report.objects.create(**SAMPLE_REPORT_1)
    
    email = TMSEmail(tms_id=456,
                     report=report,
                     subject='Foo subject',
                     body='Foo body',
                     html_body='<ul><li>Foo body</li></ul>',
                     recipient=['foo@example.com', 'bar@example.com'],
                     created_at=datetime.datetime.now(),
                     completed_at=datetime.datetime.now(),
                     status=TMSEmail.SENT,
                     purpose=TMSEmail.MANUAL_EMAIL,
                     error_message='oh no bad thing')

    converted = pdf.convert_tms_to_pdf(email)
    # ... rest of test
```

## Complete Fix for test_models.py

```python
class ReportTests(TestCase):
    test_user = None  # FIX: Don't create unsaved instance as class attribute

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        # FIX: Create and save in setUpTestData
        cls.test_user = User.objects.create(username='disposition_test_user')
        
        test_data = {
            **SAMPLE_REPORT_1.copy(),
            'retention_schedule': RetentionSchedule.objects.get(name='1 Year'),
            'location_name': 'batch disposition tests',
        }
        # ... rest of setup
```

## Error Messages You Might See

If you encounter these issues, you'll see errors like:

```
ValueError: "<Report: Report object (None)>" needs to have a value for field "id" before this relationship can be used.
```

or

```
ValueError: save() prohibited to prevent data loss due to unsaved related object 'report'.
```

## Testing Checklist

After applying fixes:

- [ ] Run: `python manage.py test utils.tests.test_pdf`
- [ ] Run: `python manage.py test cts_forms.tests.test_models`
- [ ] Run full test suite: `python manage.py test`
- [ ] Check for any other unsaved instance patterns in your codebase

## Prevention Tips

1. **Always save model instances before assigning to ForeignKey fields**
2. **Use `Model.objects.create()` instead of `Model()` + `.save()` when possible**
3. **Don't declare unsaved model instances as class attributes**
4. **In tests, use factories or `setUpTestData()` to create saved instances**
5. **If you need to test with unsaved instances, use mocking instead**

## Additional Resources

- Django 4.1 Deprecation Timeline: https://docs.djangoproject.com/en/4.1/releases/4.1/#miscellaneous
- Django 5.0 Backwards Incompatible Changes: https://docs.djangoproject.com/en/5.0/releases/5.0/#features-removed-in-5-0
- Django Model Instances Documentation: https://docs.djangoproject.com/en/5.2/ref/models/instances/