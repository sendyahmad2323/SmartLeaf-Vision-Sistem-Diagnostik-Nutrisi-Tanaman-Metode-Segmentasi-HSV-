from django.db import models

class RiwayatDeteksi(models.Model):
    nama_file = models.CharField(max_length=255)
    status_daun = models.CharField(max_length=100)
    klorofil_persen = models.FloatField()
    klorosis_persen = models.FloatField()
    kerusakan_persen = models.FloatField(default=0.0)
    catatan = models.TextField(blank=True, null=True) # Fitur tambahan untuk UPDATE
    tanggal_uji = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_file