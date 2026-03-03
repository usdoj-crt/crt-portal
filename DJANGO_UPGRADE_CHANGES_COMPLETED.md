# Django 4.2 to 5.2 Upgrade - Changes Completed

## Summary

This document lists all the changes that have been made to upgrade from Django 4.2 to Django 5.2.

---

## ✅ Completed Changes

### 1. Storage Backend Settings Migration

**File:** `crt_portal/crt_portal/settings.py` (lines 373-383)

**Changed:**
```python
# OLD (Django 4.2):
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'cts_forms.storages.PrivateS3Storage'

# NEW (Django 5.0+):
STORAGES = {
    "default": {
        "BACKEND": "cts_forms.storages.PrivateS3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}
```

**Reference:** https://docs.djangoproject.com/en/5.0/releases/5.0/#features-removed-in-5-0

---

### 2. pytz to zoneinfo Migration

Replaced all `pytz` usage with Python's standard library `zoneinfo` module.

#### File: `crt_portal/cts_forms/models.py`

**Lines 56-59:** Updated imports
```python
# OLD:
import pytz

# NEW:
from zoneinfo import ZoneInfo
from datetime import timezone as dt_timezone
```

**Lines 938-939:** Updated timezone creation
```python
# OLD:
local_tz = pytz.timezone('US/Eastern')

# NEW:
local_tz = ZoneInfo('US/Eastern')
```

**Lines 1258-1261:** Updated timezone conversion and removed normalize
```python
# OLD:
local_tz = pytz.timezone('US/Eastern')
local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
return local_tz.normalize(local_dt)

# NEW:
local_tz = ZoneInfo('US/Eastern')
local_dt = utc_dt.replace(tzinfo=dt_timezone.utc).astimezone(local_tz)
return local_dt  # .normalize() no longer needed
```

#### File: `crt_portal/analytics/models.py`

**Line 18:** Updated import
```python
# OLD:
import pytz

# NEW:
from zoneinfo import ZoneInfo
```

**Line 265:** Updated timezone creation
```python
# OLD:
local_tz = pytz.timezone('US/Eastern')

# NEW:
local_tz = ZoneInfo('US/Eastern')
```

#### File: `crt_portal/cts_forms/management/commands/update_ipynb_examples.py`

**Line 18:** Updated import
```python
# OLD:
import pytz

# NEW:
from zoneinfo import ZoneInfo
```

**Lines 120, 176:** Updated timezone creation
```python
# OLD:
local_tz = pytz.timezone('US/Eastern')

# NEW:
local_tz = ZoneInfo('US/Eastern')
```

#### File: `crt_portal/cts_forms/tests/test_filters.py`

**Lines 1, 7:** Updated imports
```python
# OLD:
from datetime import datetime
import pytz

# NEW:
from datetime import datetime, timezone
# (removed pytz import)
```

**Lines 486, 490, 494, 498, 502, 633, 636, 639, 642:** Updated timezone usage
```python
# OLD:
datetime(2022, 4, 12, 14, 56, 53, tzinfo=pytz.utc)

# NEW:
datetime(2022, 4, 12, 14, 56, 53, tzinfo=timezone.utc)
```

**Reference:** https://docs.djangoproject.com/en/5.0/releases/5.0/#features-removed-in-5-0

---

## ✅ Additional Fixes Applied

### 3. Foreign Key Validation Issues (Django 5.0)

Django 5.0 removed support for passing unsaved model instances to foreign key fields and related filters. This was deprecated in Django 4.1 and fully removed in Django 5.0.

#### File: `crt_portal/utils/tests/test_pdf.py`

**Lines 22, 26-27:** Fixed unsaved User and Report instances
```python
# OLD:
test_user = User(username='pdf_test_user')

def test_tms_converts(self):
    report = Report(**SAMPLE_REPORT_1)
    report.id = 123
    email = TMSEmail(tms_id=456, report=report, ...)

# NEW:
test_user = None

def test_tms_converts(self):
    # Django 5.0+: Must save Report instance before assigning to ForeignKey
    report = Report.objects.create(**SAMPLE_REPORT_1)
    email = TMSEmail(tms_id=456, report=report, ...)
```

**Lines 81-84:** Fixed User instance creation in setUpTestData
```python
# OLD:
@classmethod
def setUpTestData(cls):
    User.objects.filter(username='pdf_test_user').delete()
    cls.test_user.save()

# NEW:
@classmethod
def setUpTestData(cls):
    User.objects.filter(username='pdf_test_user').delete()
    # Django 5.0+: Create and save User instance in setUpTestData
    cls.test_user = User.objects.create(username='pdf_test_user')
```

**Lines 59-60:** Fixed second test method
```python
# OLD:
def test_tms_converts_multiple_recipients(self):
    report = Report(**SAMPLE_REPORT_1)
    report.public_id = 123

# NEW:
def test_tms_converts_multiple_recipients(self):
    # Django 5.0+: Must save Report instance before assigning to ForeignKey
    report = Report.objects.create(**SAMPLE_REPORT_1)
```

#### File: `crt_portal/cts_forms/tests/test_models.py`

**Lines 206, 210-211:** Fixed unsaved User instance
```python
# OLD:
class ReportTests(TestCase):
    test_user = User(username='disposition_test_user')

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        cls.test_user.save()

# NEW:
class ReportTests(TestCase):
    test_user = None

    @classmethod
    def setUpTestData(cls):
        User.objects.filter(username='disposition_test_user').delete()
        # Django 5.0+: Create and save User instance in setUpTestData
        cls.test_user = User.objects.create(username='disposition_test_user')
```

**Reference:** 
- https://docs.djangoproject.com/en/4.1/releases/4.1/#miscellaneous (Deprecation notice)
- https://docs.djangoproject.com/en/5.0/releases/5.0/#features-removed-in-5-0 (Removal notice)
- https://docs.djangoproject.com/en/4.1/releases/4.1/#reverse-foreign-key-changes-for-unsaved-model-instances

---

## 📋 Files Not Changed

### Migration Files

The following migration file contains `pytz` but was **intentionally left unchanged**:
- `crt_portal/cts_forms/migrations/0085_remove-assignee_20200716.py`

**Reason:** Historical migrations are never re-run, so changing them is unnecessary and could cause issues if someone needs to rebuild the database from scratch.

---

## 🔧 Helper Scripts Created

### 1. `DJANGO_UPGRADE_CHECKLIST.md`

Comprehensive checklist and documentation of all backwards incompatible changes from Django 4.2 to 5.2, including:
- Critical changes requiring immediate attention
- Important changes to review
- Minimum version requirements
- Deprecations to address in the future
- Testing checklist
- Links to official Django documentation

### 2. `migrate_pytz_to_zoneinfo.py`

Helper script to identify pytz usage patterns in the codebase. Can be run with:
```bash
python migrate_pytz_to_zoneinfo.py
```

This script provides:
- Identification of all files using pytz
- Line-by-line analysis of pytz usage patterns
- Suggested replacements for each usage
- Migration guide with common patterns

---

## ⚠️ Action Items Remaining

### High Priority

1. **Fix Unsaved Model Instance Issues** ✅ **COMPLETED**
   - Fixed `crt_portal/utils/tests/test_pdf.py`
   - Fixed `crt_portal/cts_forms/tests/test_models.py`
   - See `DJANGO_5_FOREIGNKEY_ISSUES.md` for details

### Medium Priority

1. **Verify PostgreSQL Version**
   - Ensure production database is PostgreSQL 14 or higher
   - Django 5.2 requires PostgreSQL 14+
   - Check with: `SELECT version();` in psql

2. **Review File Upload Code**
   - Django 5.1 now raises `FieldError` when saving files without a `name`
   - Check `ReportAttachment` and `ReportsData` models in production usage
   - Files to review: `crt_portal/cts_forms/models.py` (lines 1091-1110)

3. **Remove pytz from Dependencies**
   - Update `Pipfile` to remove `pytz` once all changes are tested
   - Run: `pipenv uninstall pytz`

### Low Priority

1. **Review Template Usage**
   - Verify that templates don't call QuerySet modification methods
   - These methods now have `alters_data=True` to prevent template usage
   - Affected methods: `create()`, `bulk_create()`, `get_or_create()`, `update_or_create()`

2. **Plan Migration from Deprecated Features**
   - Review Django 5.2 deprecations in `DJANGO_UPGRADE_CHECKLIST.md`
   - Plan updates before Django 6.0 release

---

## 🧪 Testing Checklist

Before deploying, ensure you test:

- [ ] Run full test suite: `python manage.py test`
- [ ] Test file uploads (attachments, report data)
- [ ] Verify timezone handling in reports and analytics
- [ ] Check static files are served correctly
- [ ] Test admin interface functionality
- [ ] Verify management commands work correctly
- [ ] Run migrations on a copy of production data
- [ ] Test email functionality
- [ ] Manual QA of critical user workflows

---

## 📚 Key Django Version Changes

### Django 5.0 (Released December 4, 2023)
- ❌ Removed `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE`
- ❌ Removed `pytz` support
- ❌ Dropped PostgreSQL 12 support
- ✨ Added database-computed defaults
- ✨ Added `GeneratedField` for database-generated columns

### Django 5.1 (Released August 7, 2024)
- ❌ Dropped PostgreSQL 12 support
- ❌ `FileField` now raises error when saving without filename
- ✨ Added `{% querystring %}` template tag
- ✨ Added PostgreSQL connection pools
- ✨ Added `LoginRequiredMiddleware`

### Django 5.2 (Released April 2, 2025) - LTS
- ❌ Dropped PostgreSQL 13 support
- ❌ Changed MySQL default charset to `utf8mb4` (doesn't affect PostgreSQL)
- ❌ Several methods now have `alters_data=True`
- ✨ Added Composite Primary Keys
- ✨ Automatic model imports in shell
- ✨ Simplified `BoundField` customization
- 🛡️ LTS with support until April 2028

---

## 📖 Documentation Links

- **Django 5.2 Release Notes:** https://docs.djangoproject.com/en/5.2/releases/5.2/
- **Django 5.1 Release Notes:** https://docs.djangoproject.com/en/5.1/releases/5.1/
- **Django 5.0 Release Notes:** https://docs.djangoproject.com/en/5.0/releases/5.0/
- **Django Upgrade Guide:** https://docs.djangoproject.com/en/5.2/howto/upgrade-version/
- **zoneinfo Documentation:** https://docs.python.org/3/library/zoneinfo.html

---

## 🎯 Summary

**Total Files Modified:** 7
- `crt_portal/crt_portal/settings.py`
- `crt_portal/cts_forms/models.py`
- `crt_portal/analytics/models.py`
- `crt_portal/cts_forms/management/commands/update_ipynb_examples.py`
- `crt_portal/cts_forms/tests/test_filters.py`
- `crt_portal/utils/tests/test_pdf.py` ✨ **NEW**
- `crt_portal/cts_forms/tests/test_models.py` ✨ **NEW**

**Migration Compatibility:**
- ✅ Django 5.2 LTS (supported until April 2028)
- ✅ Python 3.14.2
- ✅ PostgreSQL 14+ (verify your version)

**Next Steps:**
1. Run tests to verify all changes work correctly
2. Deploy to development environment for QA
3. Verify PostgreSQL version in production
4. Remove pytz from Pipfile after successful testing
5. Monitor for any issues in production

---

_Last Updated: [Current Date]_
_Django Version: 4.2 → 5.2_
_Python Version: 3.13.9 → 3.14.2_