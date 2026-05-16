from django.db import models

class DatasetDaun(models.Model):

    LABEL_CHOICES = [
        ('Nitrogen', 'Nitrogen (N)'),
        ('Phosphorus', 'Phosphorus (P)'),
        ('Potassium', 'Potassium (K)'),
    ]

    image = models.ImageField(upload_to='dataset/')
    label = models.CharField(max_length=50, choices=LABEL_CHOICES)

    hasil = models.CharField(max_length=100, blank=True)
    kondisi = models.CharField(max_length=100, blank=True)

    green_percent = models.FloatField(default=0)
    yellow_percent = models.FloatField(default=0)
    brown_percent = models.FloatField(default=0)

    accuracy = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label