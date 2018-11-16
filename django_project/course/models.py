from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        """String for representing the Model object."""
        return self.title
