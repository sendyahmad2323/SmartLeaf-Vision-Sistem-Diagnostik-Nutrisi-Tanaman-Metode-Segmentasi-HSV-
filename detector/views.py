import os
import cv2
import numpy as np

from django.shortcuts import render, redirect
from .models import DatasetDaun
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# =========================================
# PROSES HSV
# =========================================

def proses_hsv(path_gambar):

    # baca gambar
    image = cv2.imread(path_gambar)
    if image is None:
        return None

    # resize
    image = cv2.resize(image, (500, 500))

    # preprocessing
    blur = cv2.GaussianBlur(image, (5, 5), 0)

    # RGB -> HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # =========================================
    # HSV RANGE (Berdasarkan Tabel 3.2 Laporan)
    # =========================================

    # hijau
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    # kuning
    lower_yellow = np.array([20, 40, 40])
    upper_yellow = np.array([35, 255, 255])

    # coklat
    lower_brown = np.array([10, 40, 20])
    upper_brown = np.array([20, 255, 200])

    # =========================================
    # SEGMENTASI HSV
    # =========================================

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)

    # =========================================
    # EKSTRAKSI FITUR HSV (PERSENTASE)
    # =========================================

    green_pixels = cv2.countNonZero(mask_green)
    yellow_pixels = cv2.countNonZero(mask_yellow)
    brown_pixels = cv2.countNonZero(mask_brown)

    total_leaf = green_pixels + yellow_pixels + brown_pixels

    if total_leaf == 0:
        total_leaf = 1

    green_percent = round((green_pixels / total_leaf) * 100, 2)
    yellow_percent = round((yellow_pixels / total_leaf) * 100, 2)
    brown_percent = round((brown_pixels / total_leaf) * 100, 2)

    # =========================================
    # DIAGNOSTIK NUTRISI (MENCARI NILAI DOMINAN)
    # Sesuai dengan penjelasan di Bab 5.2 Laporan
    # =========================================
    
    if yellow_percent > green_percent and yellow_percent > brown_percent:
        hasil = "Nitrogen"
        kondisi = "Klorosis / Daun Menguning"
        confidence = yellow_percent

    elif brown_percent > green_percent and brown_percent > yellow_percent:
        hasil = "Potassium"
        kondisi = "Nekrosis / Bercak Coklat"
        confidence = brown_percent

    else:
        # Jika hijau dominan, sistem memvonis sebagai Phosphorus
        hasil = "Phosphorus"
        kondisi = "Hijau Gelap / Keunguan"
        confidence = green_percent

    return {
        'hasil': hasil,
        'kondisi': kondisi,
        'green': green_percent,
        'yellow': yellow_percent,
        'brown': brown_percent,
        'accuracy': confidence, 
    }


# =========================================
# HALAMAN HOME
# =========================================

def index(request):
    total = DatasetDaun.objects.count()
    return render(request, 'detector/index.html', {
        'total': total
    })


# =========================================
# PROSES DATASET KAGGLE
# =========================================

def proses_dataset(request):
    dataset_path = 'media/dataset/'

    # Label kelas yang diproses sesuai Tabel 3.1
    labels = [
        'Nitrogen',
        'Phosphorus',
        'Potassium'
    ]
    
    total_data = 0

    DatasetDaun.objects.all().delete()

    for label in labels:
        folder_path = os.path.join(dataset_path, label)

        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                hasil = proses_hsv(file_path)

                if hasil is None:
                    continue

                prediksi = hasil['hasil']

                # =====================================
                # SAVE DATABASE
                # =====================================
                DatasetDaun.objects.create(
                    image='dataset/' + label + '/' + filename,
                    label=label,
                    hasil=prediksi,
                    kondisi=hasil['kondisi'],
                    green_percent=hasil['green'],
                    yellow_percent=hasil['yellow'],
                    brown_percent=hasil['brown'],
                )
                
                total_data += 1

    # Mengarahkan ke halaman success yang baru kita desain
    return render(request, 'detector/success.html', {
        'total_data': total_data
    })


# =========================================
# DASHBOARD
# =========================================

def dashboard(request):
    data = DatasetDaun.objects.all()

    y_true = []
    y_pred = []

    for item in data:
        y_true.append(item.label)
        y_pred.append(item.hasil)

    # zero_division=0 untuk menghindari error saat database kosong
    accuracy = accuracy_score(y_true, y_pred) * 100 if len(y_true) > 0 else 0
    
    precision = precision_score(
        y_true, y_pred, average='macro', zero_division=0
    ) * 100

    recall = recall_score(
        y_true, y_pred, average='macro', zero_division=0
    ) * 100

    f1 = f1_score(
        y_true, y_pred, average='macro', zero_division=0
    ) * 100

    # Menyusun Confusion Matrix
    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=["Nitrogen", "Phosphorus", "Potassium"]
    )

    return render(request, 'detector/dashboard.html', {
        'data': data,
        'total_data': data.count(),
        'accuracy': round(accuracy, 2),
        'precision': round(precision, 2),
        'recall': round(recall, 2),
        'f1': round(f1, 2),
        'confusion_matrix': cm.tolist()
    })


# =========================================
# FUNGSI LAINNYA
# =========================================

def edit_deteksi(request, id):
    return redirect('dashboard')

def hapus_deteksi(request, id):
    return redirect('dashboard')