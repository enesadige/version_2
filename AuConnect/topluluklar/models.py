from django.db import models

# Create your models here.

class Topluluklar(models.Model):
    name = models.CharField(max_length=100)
    img = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


    def get_image_path(self):
        return "/img/" + str(self.img)
    