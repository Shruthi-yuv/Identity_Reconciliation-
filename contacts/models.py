from django.db import models

# Create your models here.


class Contact(models.Model):
    phoneNumber = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    linkedId = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    linkPrecedence = models.CharField(
        max_length=10, choices=[('primary', 'primary'), ('secondary', 'secondary')], default='primary'
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    deletedAt = models.DateTimeField(null=True, blank=True)

    def _str_(self):
        return f"Contact ID: {self.id} - {self.email or self.phoneNumber}"

    class Meta:
        ordering = ['createdAt']