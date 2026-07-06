# 🌿 SmartLeaf Vision
### Plant Leaf Nutrient Diagnosis Using HSV Color Segmentation

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Django](https://img.shields.io/badge/Django-Framework-green)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-Frontend-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

SmartLeaf Vision is a Computer Vision project developed to identify plant nutrient deficiencies using **HSV Color Segmentation**.

The application analyzes leaf images, extracts dominant color features, and predicts nutrient deficiency based on HSV color distribution.

---

# 📖 Overview

Healthy and unhealthy leaves usually have different color characteristics.

This project applies image processing techniques to separate leaf colors into several categories:

- 🟢 Green
- 🟡 Yellow
- 🟤 Brown

The extracted color percentage is then used to determine possible nutrient deficiencies.

---

# ✨ Features

- Upload leaf images
- HSV color segmentation
- RGB → HSV conversion
- Green, Yellow, Brown detection
- Automatic nutrient diagnosis
- Interactive dashboard
- Color percentage visualization
- Performance evaluation

---

# 🛠️ Technologies

- Python
- Django
- OpenCV
- NumPy
- Bootstrap
- SQLite / MySQL

---

# ⚙️ Image Processing Pipeline

```text
Input Image
      │
      ▼
Resize
      │
      ▼
Gaussian Blur
      │
      ▼
RGB → HSV
      │
      ▼
HSV Segmentation
      │
      ▼
Color Feature Extraction
      │
      ▼
Rule-Based Diagnosis
      │
      ▼
Dashboard Result
```

---

# 📊 Dataset

Dataset Source:

- Kaggle Plant Leaf Dataset

Number of images:

- 216 Images

Classes:

| Nutrient | Condition |
|----------|-----------|
| Nitrogen | Yellow Leaf |
| Phosphorus | Dark Green / Purple |
| Potassium | Brown Spots |

---

# 📈 Evaluation Result

| Metric | Score |
|---------|-------|
| Accuracy | 52.31% |
| Precision | 35.64% |
| Recall | 35.43% |
| F1-Score | 32.63% |

---

# 📂 Project Structure

```
SmartLeafVision/
│
├── dataset/
├── media/
├── static/
├── templates/
├── app/
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

Clone repository

```bash
git clone https://github.com/username/SmartLeafVision.git
```

Go to project

```bash
cd SmartLeafVision
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run server

```bash
python manage.py runserver
```

Open browser

```
http://127.0.0.1:8000
```

---

# 🖼️ Application Preview

> Add screenshots here

```
Home Page

Dashboard

HSV Segmentation

Diagnosis Result
```

---

# 👨‍💻 Team

Kelompok 1

- Sendy Ahmad
- Chandra Dvaipayana
- Teuku M Fariz Sarbaini Meuraxa
- Muhammad Bustami
- Muna Khalishah Fatwa Fathiyyah

---

# 📚 Course

Computer Vision

Faculty of Science and Technology

Universitas Muhammadiyah Kalimantan Timur

2026
