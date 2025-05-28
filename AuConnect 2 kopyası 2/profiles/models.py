from django.db import models
from django.contrib.auth.models import User
from topluluklar.models import Topluluklar

class Follow(models.Model):
    """
    Bir öğrencinin bir topluluğu takip etmesi için model.
    Öğrenci (User) ile topluluk arasında çoka çok ilişki kurar.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    topluluk = models.ForeignKey(Topluluklar, on_delete=models.CASCADE, related_name='followers')
    date_followed = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Takip"
        verbose_name_plural = "Takipler"
        # Aynı kullanıcının aynı topluluğu birden fazla takip etmesini önle
        unique_together = ('user', 'topluluk')

    def __str__(self):
        return f"{self.user.username} → {self.topluluk.name}"
