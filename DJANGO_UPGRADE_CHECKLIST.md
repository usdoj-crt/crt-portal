# Django 4.2 to 5.2 Upgrade Checklist

This document outlines the backwards incompatible changes and required actions when upgrading from Django 4.2 to Django 5.2.

## Overview

We upgraded from:
- Django 4.2 → 5.2
- Python 3.13.9 → 3.14.2

Django 5.2 is a Long-Term Support (LTS) release with support until at least April 2028.

## Critical Changes Required

### 1. Storage Backend Settings (Django 5.0) - **ACTION REQUIRED**

**Status:** ⚠️ NEEDS IMMEDIATE ATTENTION

The `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` settings have been removed.

**Current Code (settings.py:377-378):**
```python
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'cts_forms.storages.PrivateS3Storage'
```

**Required Change:**
```python
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

### 2. pytz Usage - **ACTION REQUIRED**

**Status:** ⚠️ NEEDS IMMEDIATE ATTENTION

Support for `pytz` was removed in Django 5.0. Must migrate to `zoneinfo`.

**Files Using pytz:**
- `crt_portal/analytics/models.py:19`
- `crt_portal/cts_forms/management/commands/update_ipynb_examples.py:19`
- `crt_portal/cts_forms/migrations/0085_remove-assignee_20200716.py:5`
- `crt_portal/cts_forms/models.py:58`
- `crt_portal/cts_forms/tests/test_filters.py:10`

**Required Changes:**
```python
# OLD:
import pytz
eastern = pytz.timezone('US/Eastern')
dt = eastern.localize(datetime(2024, 1, 1))

# NEW:
from zoneinfo import ZoneInfo
eastern = ZoneInfo('US/Eastern')
dt = datetime(2024, 1, 1, tzinfo=eastern)
```

**Reference:** https://docs.djangoproject.com/en/5.0/releases/5.0/#features-removed-in-5-0

---

### 3. PostgreSQL Version Support

**Status:** ✅ OK (assuming PostgreSQL 14+)

- Django 5.1 dropped support for PostgreSQL 12
- Django 5.2 dropped support for PostgreSQL 13
- Minimum supported: PostgreSQL 14

**Action:** Verify your PostgreSQL version is 14 or higher.

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#dropped-support-for-postgresql-13

---

### 4. MySQL Character Set Default (Django 5.2)

**Status:** ✅ N/A (using PostgreSQL)

MySQL connections now default to `utf8mb4` instead of `utf8`. Not applicable since this project uses PostgreSQL.

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#changed-mysql-connection-character-set-default

---

## Important Changes to Review

### 5. File Upload Changes (Django 5.1) - **REVIEW RECOMMENDED**

**Status:** ⚠️ REVIEW REQUIRED

`FileField` now raises `FieldError` when saving a file without a `name`.

**Files to Review:**
- `crt_portal/cts_forms/models.py` (ReportAttachment, ReportsData models)

**Action:** Ensure all file uploads include a proper filename before saving.

**Reference:** https://docs.djangoproject.com/en/5.1/releases/5.1/#miscellaneous

---

### 6. Template Context Processor (Django 5.2)

**Status:** ✅ OK

The `debug()` context processor is no longer included in default project templates, but your settings already don't rely on it being present by default.

**Current settings.py shows explicit context processors listed - no changes needed.**

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#miscellaneous

---

### 7. Admin Exceptions Import Path (Django 5.0)

**Status:** ✅ OK (not used in codebase)

`AlreadyRegistered` and `NotRegistered` moved from `django.contrib.admin.sites` to `django.contrib.admin.exceptions`.

No changes needed - not currently used in the codebase.

**Reference:** https://docs.djangoproject.com/en/5.0/releases/5.0/#miscellaneous

---

### 8. HttpRequest.accepted_types Ordering (Django 5.2)

**Status:** ✅ OK (not used in codebase)

`HttpRequest.accepted_types` is now sorted by client's preference. Not currently used in codebase.

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#miscellaneous

---

### 9. EmailMultiAlternatives.alternatives (Django 5.2)

**Status:** ✅ OK (not found in codebase)

Adding alternatives is now only supported via `attach_alternative()` method. Not currently used in the codebase.

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#miscellaneous

---

### 10. Methods with alters_data=True (Django 5.2)

**Status:** ⚠️ REVIEW IF USING IN TEMPLATES

Several methods now have `alters_data=True` to prevent side effects when rendering templates:
- `QuerySet.create()`, `acreate()`
- `QuerySet.bulk_create()`, `abulk_create()`
- `QuerySet.get_or_create()`, `aget_or_create()`
- `QuerySet.update_or_create()`, `aupdate_or_create()`
- `UserManager.create_user()`, `acreate_user()`
- `UserManager.create_superuser()`, `acreate_superuser()`

**Action:** Review templates to ensure these methods aren't being called during template rendering.

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#miscellaneous

---

## Minimum Version Requirements

### Python
- **Minimum:** Python 3.10
- **Current:** Python 3.14.2 ✅
- **Supported:** 3.10, 3.11, 3.12, 3.13, 3.14

### Database
- **PostgreSQL:** 14+ (you're likely on 14+) ✅

### Third-party Libraries
- **asgiref:** ≥ 3.8.1 (was 3.7.0)
- **selenium:** ≥ 4.8.0 (was 3.8.0)
- **SQLite:** ≥ 3.31.0 (was 3.27.0)
- **gettext:** ≥ 0.19 (was 0.15)
- **oracledb:** ≥ 2.3.0 (was 1.3.2) - N/A for PostgreSQL
- **colorama:** ≥ 0.4.6
- **docutils:** ≥ 0.19

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#python-compatibility

---

## Deprecations to Address (Not Breaking Yet)

### Django 5.2 Deprecations

These are deprecated but still work. Plan to address before Django 6.0:

1. **ModelAdmin.log_deletion()** → Use `ModelAdmin.log_deletions()` (plural)
2. **django.utils.itercompat.is_iterable()** → Use `isinstance(..., collections.abc.Iterable)`
3. **GeoIP2.coords()** → Use `GeoIP2.lon_lat()`
4. **GeoIP2.open()** → Use `GeoIP2` constructor
5. **Model.save() positional arguments** → Use keyword-only arguments
6. **CheckConstraint(check=...)** → Use `CheckConstraint(condition=...)`

**Reference:** https://docs.djangoproject.com/en/5.2/releases/5.2/#features-deprecated-in-5-2

---

## Testing Checklist

- [ ] Run full test suite
- [ ] Test file uploads (ReportAttachment, ReportsData)
- [ ] Test timezone handling after pytz migration
- [ ] Verify static files are served correctly with new STORAGES setting
- [ ] Test admin interface functionality
- [ ] Test any custom management commands
- [ ] Verify database migrations apply cleanly
- [ ] Test email functionality if using EmailMultiAlternatives
- [ ] Review any custom template tags/filters that might call queryset methods

---

## Migration Steps

1. **Update Pipfile**
   - ✅ Already done: Django==5.2

2. **Update Storage Settings**
   - ⚠️ Required: Migrate `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` to `STORAGES`

3. **Replace pytz with zoneinfo**
   - ⚠️ Required: Update all imports and usage

4. **Update Dependencies**
   ```bash
   pipenv update
   ```

5. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run Tests**
   ```bash
   python manage.py test
   ```

7. **Deploy to Development**
   - Test thoroughly in dev environment first

---

## New Features You May Want to Use

### Django 5.2
- **Composite Primary Keys** - Multi-field primary keys
- **Automatic model imports in shell** - Models auto-imported in `manage.py shell`
- **Simplified BoundField customization** - Easier form rendering customization
- **JSONArray database function** - New aggregation function

### Django 5.1
- **{% querystring %}** template tag - Easier URL query parameter manipulation
- **PostgreSQL connection pools** - Improved performance
- **LoginRequiredMiddleware** - Require authentication by default

### Django 5.0
- **Database-computed defaults** - `db_default` parameter for fields
- **GeneratedField** - Database-generated columns
- **Facet filters in admin** - Show counts for filters

**References:**
- https://docs.djangoproject.com/en/5.2/releases/5.2/#what-s-new-in-django-5-2
- https://docs.djangoproject.com/en/5.1/releases/5.1/#what-s-new-in-django-5-1
- https://docs.djangoproject.com/en/5.0/releases/5.0/#what-s-new-in-django-5-0

---

## Summary of Required Actions

| Priority | Action | Status |
|----------|--------|--------|
| **HIGH** | Migrate `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` to `STORAGES` dict | ⚠️ Required |
| **HIGH** | Replace all `pytz` usage with `zoneinfo` | ⚠️ Required |
| **MEDIUM** | Review file upload code for missing filenames | ⚠️ Review |
| **MEDIUM** | Verify PostgreSQL version is 14+ | ⚠️ Verify |
| **LOW** | Review template usage of QuerySet modification methods | ⚠️ Review |
| **LOW** | Plan migration away from deprecated features | 📋 Plan |

---

## Additional Resources

- **Django 5.2 Release Notes:** https://docs.djangoproject.com/en/5.2/releases/5.2/
- **Django 5.1 Release Notes:** https://docs.djangoproject.com/en/5.1/releases/5.1/
- **Django 5.0 Release Notes:** https://docs.djangoproject.com/en/5.0/releases/5.0/
- **Django Upgrade Guide:** https://docs.djangoproject.com/en/5.2/howto/upgrade-version/

---

## Notes

- Django 5.2 is an LTS release with security updates until at least April 2028
- Django 4.2 LTS support ends in April 2026
- No breaking changes were found for your usage of CharField (max_length is still required except on SQLite)
- No issues found with admin, forms, or model constraints in your codebase