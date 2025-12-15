from django.db import models
from django.utils.text import slugify

class UniqueSlugMixin(models.Model):
    """
    Mixin to automatically generate a unique slug from a 'name' field.
    """
    class Meta:
        abstract = True

    def _generate_unique_slug(self):
        """
        Create a URL-safe slug from name and ensure uniqueness by adding -2, -3, ...
        Only called when slug is empty.
        """
        base = slugify(self.name) or "item"
        maxlen = self._meta.get_field("slug").max_length or 50
        slug = base[:maxlen]

        # If taken, append -2, -3 ... truncating base to keep within maxlen
        counter = 2
        # Use self.__class__ to query the correct model
        while self.__class__.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            suffix = f"-{counter}"
            slug = f"{base[:maxlen - len(suffix)]}{suffix}"
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)
