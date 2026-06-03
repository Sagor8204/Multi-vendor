from django.db import models
from django.conf import settings

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class SEOMixin(models.Model):
    meta_title = models.CharField(max_length=255, blank=True, null=True, help_text="Search engine title")
    meta_description = models.TextField(blank=True, null=True, help_text="Search engine description")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated keywords")
    
    # Open Graph Tags for Social Media
    og_title = models.CharField(max_length=255, blank=True, null=True)
    og_description = models.TextField(blank=True, null=True)
    og_image = models.FileField(upload_to="seo/", blank=True, null=True)

    class Meta:
        abstract = True

    def get_meta_title(self):
        # Fallback to the object's name if meta_title is empty
        return self.meta_title or getattr(self, 'name', getattr(self, 'store_name', str(self)))

class File(BaseModel):
    file = models.FileField(upload_to='images/')
    file_type = models.CharField(max_length=50, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
