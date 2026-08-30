<div align="center">

# 🖥️ Ngga Tutu

### ⚡ PC Performance Benchmark Suite

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![Browser](https://img.shields.io/badge/Browser-Lite版-FF6B6B?style=for-the-badge&logo=googlechrome&logoColor=white)

<br>

**Stres testi yap, gerçek performansı ölç, profesyonel puan al.**

**Stress test your PC, measure real performance, get a professional grade.**

[🚀 Web Lite](#-browser-lite-version-web) · [📦 Kurulum](#-kurulum--installation) · [✨ Özellikler](#-özellikler--features) · [📊 Kullanım](#-kullanım--usage) · [🤝 Katkı](#-nasıl-katkı-sağlanır--how-to-contribute)

</div>

---

## 🌐 Browser Lite Version (Web)

> 🌍 **Tüm cihazlarda çalışır** — Sadece bir tarayıcı yeterli!
> 🌍 **Works on all devices** — Just a browser is enough!

| 🖥️ Windows | 🍎 macOS | 📱 Android | 📱 iOS | 🐧 Linux |
|:---:|:---:|:---:|:---:|:---:|
| ✅ | ✅ | ✅ | ✅ | ✅ |

**💡 Lite sürümü neler yapar:**

| Test | Açıklama | Gerçek Test |
|:---:|---|:---:|
| ⚡ **CPU** | Asal sayılar, matris çarpma, SHA-256 hash, sıralama | ✅ |
| 🧠 **Memory** | Sıralı/rastgele okuma-yazma, Float64 bant genişliği | ✅ |
| 🎮 **GPU** | 10K+ shape, piksel işleme, gradyan, WebGL | ✅ |
| 💾 **Disk** | Blob yazma/okuma, JSON serialize, gzip sıkıştırma | ✅ |

> 📁 Tek dosya: `index.html` — GitHub Pages üzerinden çalışır
> 🔗 **[Canlı Demo →](https://m-k-b-61.github.io/nggatutu/)**

---

## 📦 Kurulum / Installation

### 🐍 Python Sürümü (Windows Only)

```bash
git clone https://github.com/M-K-B-61/nggatutu.git
cd nggatutu
pip install -r requirements.txt
python main.py
```

> 📌 İlk çalıştırmada bağımlılıklar otomatik yüklenir.
> 📌 Dependencies install automatically on first run.

### 🌐 Browser Lite Sürümü

Hiçbir kurulum gerekmez! `index.html` dosyasını tarayıcınızda açmanız yeterli.

> No installation needed! Just open `index.html` in your browser.

---

## ✨ Özellikler / Features

<table>
<tr>
<td width="50%">

### ⚡ CPU Benchmark
- Asal Sayı Testi (5M — Sieve of Eratosthenes)
- Matris Çarpma (256×256 Float32)
- SHA-256 Kripto Hash (5000 iterasyon)
- Dizi Sıralama (2M eleman)
- Tek & Çok çekirdek desteği

</td>
<td width="50%">

### 🧠 Memory Benchmark
- Sıralı Okuma/Yazma
- Rastgele Erişim
- Float64 Bant Genişliği
- Kopyalama Hızı
- Cache Performansı
- Gecikme Ölçümü

</td>
</tr>
<tr>
<td>

### 💾 Disk Benchmark
- Sıralı Okuma/Yazma
- Rastgele 4K Okuma/Yazma
- IOPS Ölçümü
- Karışık İş Yükü
- Gecikme Testi

</td>
<td>

### 🎮 GPU Benchmark
- 1920×1080 2D Rendering
- 10,000+ Şekil Çizimi
- Pikel İşleme (edge detection)
- WebGL Shader Testi
- FPS / Frame Time Analizi
- Gerçek Zamanlı HUD

</td>
</tr>
</table>

---

## 📊 Puanlama Sistemi / Score System

Benchmark sonuçları **S** (en iyi) ile **E** (en kötü) arasında derecelendirilir:

| Derece | Açıklama | Description |
|:---:|---|---|
| **🏆 S** | Tutkun / Fazla | Enthusiast / Overkill |
| **🥇 A** | Üst Düzey | High-End |
| **🥈 B** | Orta Düzey | Mid-Range |
| **🥉 C** | Giriş Seviyesi | Entry-Level |
| **⚠️ D** | Ortalamanın Altı | Below Average |
| **❌ E** | Yükseltme Gerekli | Needs Upgrade |

---

## 🎯 Profiller / Profiles

| Profil | Açıklama | Süre |
|:---:|---|:---:|
| `quick` | Hızlı test | ~30sn |
| `full` | Tam benchmark paketi | ~5dk |
| `gaming` | GPU odaklı + CPU/RAM | ~3dk |
| `productivity` | CPU/RAM odaklı | ~3dk |
| `stress` | Uzun süreli stres testi | ~30dk |

---

## 📊 Kullanım / Usage

```bash
# 🖥️ GUI başlat
python main.py

# 💻 CLI — tüm testleri çalıştır
python main.py cli

# ⚡ Bireysel testler
python main.py cpu
python main.py memory
python main.py disk
python main.py gpu

# ℹ️ Sistem bilgisi
python main.py info

# 🎯 Benchmark profilleri
python main.py profiles

# 📜 Geçmiş sonuçlar
python main.py history

# 📌 Versiyon
python main.py version
```

---

## 📁 Proje Yapısı / Project Structure

```
nggatutu/
├── main.py                 # GUI + CLI giriş noktası
├── requirements.txt        # Bağımlılıklar
├── index.html              # 🌐 Browser Lite Benchmark
├── README.md
├── benchmarks/
│   ├── __init__.py
│   ├── cpu.py              # CPU benchmark paketi
│   ├── memory.py           # Memory benchmark paketi
│   ├── disk.py             # Disk benchmark paketi
│   ├── gpu.py              # GPU benchmark paketi
│   ├── system_info.py      # Donanım tespiti
│   ├── scores.py           # Puanlama sistemi
│   ├── history.py          # Sonuç geçmişi
│   ├── profiles.py         # Benchmark profilleri
│   ├── stress.py           # Stres testleri
│   ├── health.py           # Sistem sağlık durumu
│   ├── monitor.py          # Gerçek zamanlı izleme
│   └── reports.py          # Rapor oluşturma
└── benchmark_history/      # Kaydedilmiş sonuçlar
```

---

## 🤝 Nasıl Katkı Sağlanır / How to Contribute

1. 🍴 Deposu fork edin
2. 📝 Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. 💾 Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. 🚀 Branch'e push edin (`git push origin feature/amazing-feature`)
5. 📬 Pull Request açın

---

## 👥 Contributors

| | Katılımcı | Rol | GitHub |
|:---:|:---:|:---:|:---:|
| 👑 | **M-K-B-61** | 🎯 Lead Developer (Oflu) | [@M-K-B-61](https://github.com/M-K-B-61) |
| 🔥 | **anotherphonker** | 💻 Developer (Mr. Ng Ga) | [@anotherphonker](https://github.com/anotherphonker) |

<div align="center">

<a href="https://github.com/M-K-B-61/nggatutu/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=M-K-B-61/nggatutu" />
</a>

</div>

---

## 📜 Lisans / License

Bu proje [MIT](LICENSE) lisansı altında dağıtılır.

This project is distributed under the [MIT](LICENSE) license.

---

<div align="center">

**⚡ Ngga Tutu** — *Gerçek Performans, Gerçek Puan*

Made with 🐍 Python · 🎨 PySide6 · 🔢 NumPy · 🎮 Pygame · 🌐 HTML5

[⬆️ Üste Dön / Back to Top](#-ngga-tutu)

</div>
