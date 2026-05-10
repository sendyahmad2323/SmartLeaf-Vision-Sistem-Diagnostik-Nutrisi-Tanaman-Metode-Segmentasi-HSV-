from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import RiwayatDeteksi
import cv2
import numpy as np
import os
import uuid

def analyze_leaf(image_path):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 1. Masker Daun Keseluruhan (Diperluas mencakup warna pucat, gelap, dan kering)
    # Rentang Hue 0-100 mencakup semua spektrum warna daun (merah, coklat, kuning, hijau)
    lower_leaf = np.array([0, 15, 15]) 
    upper_leaf = np.array([100, 255, 255])
    leaf_mask = cv2.inRange(hsv, lower_leaf, upper_leaf)
    total_leaf_pixels = cv2.countNonZero(leaf_mask)
    
    if total_leaf_pixels == 0:
        return "Gagal Dianalisis", "Objek daun tidak jelas.", "secondary", 0, 0, 0, [], [], [], ""
    
    kernel = np.ones((5,5), np.uint8)

    # 2. Masking HIJAU (Klorofil)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pct = (cv2.countNonZero(green_mask) / total_leaf_pixels) * 100

    # 3. Masking KUNING (Klorosis)
    # Saturation dinaikkan (50) agar daun kering pucat tidak numpang lewat dibaca kuning
    lower_yellow = np.array([15, 50, 100]) 
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    yellow_mask_clean = cv2.morphologyEx(cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel), cv2.MORPH_CLOSE, kernel)
    yellow_pct = (cv2.countNonZero(yellow_mask_clean) / total_leaf_pixels) * 100

    # 4. Masking COKLAT / MATI (Logika Eksklusi Cerdas)
    # Semua bagian daun yang BUKAN HIJAU dan BUKAN KUNING = Jaringan Rusak/Mati
    healthy_and_yellow_mask = cv2.bitwise_or(green_mask, yellow_mask_clean)
    brown_mask = cv2.bitwise_and(leaf_mask, cv2.bitwise_not(healthy_and_yellow_mask))
    brown_mask_clean = cv2.morphologyEx(cv2.morphologyEx(brown_mask, cv2.MORPH_OPEN, kernel), cv2.MORPH_CLOSE, kernel)
    brown_pct = (cv2.countNonZero(brown_mask_clean) / total_leaf_pixels) * 100

    # === BOUNDING BOX & KONTUR ===
    img_annotated = img.copy()
    
    # Deteksi & Kotak Merah untuk Kuning (Klorosis)
    contours_yellow, _ = cv2.findContours(yellow_mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_yellow:
        if cv2.contourArea(cnt) > 300: 
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img_annotated, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(img_annotated, 'Klorosis', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Deteksi & Kotak Biru untuk Coklat/Mati (Nekrosis)
    # Karena area mati bisa sangat besar (seperti di fotomu), kita beri kotak pembatas utama
    contours_brown, _ = cv2.findContours(brown_mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_brown:
        if cv2.contourArea(cnt) > 500: # Batas area diperbesar agar noise tidak ikut dikotak
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img_annotated, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(img_annotated, 'Nekrosis', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Simpan gambar beranotasi
    annotated_filename = f"annotated_{uuid.uuid4().hex}.jpg"
    annotated_path = os.path.join(os.path.dirname(image_path), annotated_filename)
    cv2.imwrite(annotated_path, img_annotated)
    annotated_url = f"/media/{annotated_filename}"
    
    # Ekstraksi Histogram RGB
    hist_r = cv2.calcHist([img_rgb], [0], leaf_mask, [256], [0, 256]).flatten().tolist()
    hist_g = cv2.calcHist([img_rgb], [1], leaf_mask, [256], [0, 256]).flatten().tolist()
    hist_b = cv2.calcHist([img_rgb], [2], leaf_mask, [256], [0, 256]).flatten().tolist()
    
    # Logika Status Diagnosis
    if brown_pct > 15: # Jika jaringan mati lebih dari 15%
        status = "Kerusakan Jaringan (Nekrosis)"
        advice = "Daun mengalami nekrosis/kematian jaringan parah. Segera buang daun yang terinfeksi."
        color_class = "danger"
    elif yellow_pct > 25:
        status = "Defisiensi Nitrogen (Klorosis)"
        advice = "Daun klorosis (menguning). Segera aplikasikan pupuk tinggi Nitrogen (Urea)."
        color_class = "warning"
    elif green_pct > 60:
        status = "Sehat & Optimal"
        advice = "Klorofil sangat baik. Lanjutkan perawatan rutin."
        color_class = "success"
    else:
        status = "Defisiensi Ringan"
        advice = "Warna daun tidak merata. Tambahkan pupuk NPK dan periksa pH tanah."
        color_class = "info"
        
    return status, advice, color_class, round(green_pct, 1), round(yellow_pct, 1), round(brown_pct, 1), hist_r, hist_g, hist_b, annotated_url

def index(request):
    context = {'results': request.session.get('hasil_terakhir', [])}
    if request.method == 'POST' and request.FILES.getlist('images'):
        fs = FileSystemStorage()
        hasil_baru = []
        for index_loop, f in enumerate(request.FILES.getlist('images')):
            filename = fs.save(f.name, f)
            file_path = fs.path(filename)
            
            status, advice, clr_class, green, yellow, brown, hr, hg, hb, ann_url = analyze_leaf(file_path)
            
            # Update simpan ke database dengan field coklat
            RiwayatDeteksi.objects.create(
                nama_file=f.name, status_daun=status, 
                klorofil_persen=green, klorosis_persen=yellow, kerusakan_persen=brown
            )
            
            hasil_baru.append({
                'id_loop': index_loop, 'name': f.name, 'url': ann_url,
                'status': status, 'advice': advice, 'color_class': clr_class,
                'green_pct': green, 'yellow_pct': yellow, 'brown_pct': brown,
                'hist_r': hr, 'hist_g': hg, 'hist_b': hb 
            })
            
        request.session['hasil_terakhir'] = hasil_baru
        context['results'] = hasil_baru
    return render(request, 'detector/index.html', context)

# ... (Biarkan fungsi dashboard, edit_deteksi, hapus_deteksi, reset_pemindai sama seperti sebelumnya) ...

def dashboard(request):
    data_riwayat = RiwayatDeteksi.objects.all().order_by('-tanggal_uji')
    jml_sehat = data_riwayat.filter(status_daun="Sehat & Optimal").count()
    jml_nitrogen = data_riwayat.filter(status_daun="Defisiensi Nitrogen (N)").count()
    jml_lainnya = data_riwayat.filter(status_daun="Defisiensi Lainnya").count()
    
    context = {'riwayat': data_riwayat, 'chart_data': [jml_sehat, jml_nitrogen, jml_lainnya]}
    return render(request, 'detector/dashboard.html', context)


def edit_deteksi(request, id):
    data = get_object_or_404(RiwayatDeteksi, id=id)
    if request.method == 'POST':
        data.catatan = request.POST.get('catatan')
        data.save()
        messages.success(request, 'Catatan berhasil diperbarui!')
    return redirect('dashboard')


def hapus_deteksi(request, id):
    data = get_object_or_404(RiwayatDeteksi, id=id)
    nama_file_dihapus = data.nama_file
    data.delete()
    
    session_data = request.session.get('hasil_terakhir', [])
    session_baru = [item for item in session_data if item['name'] != nama_file_dihapus]
    request.session['hasil_terakhir'] = session_baru
    
    messages.success(request, f'Data {nama_file_dihapus} berhasil dihapus dari sistem!')
    return redirect('dashboard')


def reset_pemindai(request):
    if 'hasil_terakhir' in request.session:
        del request.session['hasil_terakhir']
    return redirect('index')