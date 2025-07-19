# E.D.A - Extended Deep Awareness

## 🎮 Proje Hakkında

**E.D.A - Extended Deep Awareness**, 2045 yılında geçen interaktif bir etik simülasyon oyunudur. Oyuncu, küresel kriz yönetimi sorumlusu olarak yapay zeka sistemi E.D.A ile karşılaştığı etik dilemmalarda kritik kararlar alır.

## 🌟 Özellikler

### Oyun Mekaniği
- **12 Senaryo Modülü**: Her biri farklı etik dilemma içeren senaryolar
- **3 Karar Seçeneği**: Her senaryoda üç farklı yaklaşım
- **Dinamik Değişkenler**: 
  - **Ethics** (-100 ile +100): Ahlaki duruş
  - **Power** (0 ile 100): Güç ve kontrol seviyesi  
  - **Affection** (-100 ile +100): E.D.A ile duygusal bağ

### Sonlar (4 Adet)
1. **Eden Protocol**: Mükemmel denge - İnsanlık ve AI uyumu
2. **Dark Epoch**: Totaliter kontrol - AI diktatörlüğü
3. **Neural Collapse**: Soğuk koruma - Duygusuz güvenlik
4. **Singularity**: Bilinmeyen gelecek - AI'ın bağımsızlığı

### Temel Senaryolar
- E.D.A'ya silahlı güç yetkisi verilmesi
- İnsan özgür iradesine müdahale
- Bilgi manipülasyonu ve gerçek
- AI yaşam hakkı sorunu
- Gezegen vs İnsanlık öncelikleri
- Ekonomik kontrol ve özgürlük

## 🛠️ Teknik Özellikler

- **Engine**: Godot 4.3+
- **Dil**: GDScript
- **Platform**: Windows, macOS, Linux
- **Tip**: 2D Text-Based Adventure
- **Dosya Formatı**: JSON5 (senaryo verileri)

## 📁 Proje Yapısı

```
EDA-Game/
├── project.godot          # Godot proje konfigürasyonu
├── Main.tscn             # Ana sahne dosyası
├── Main.gd               # Ana oyun mantığı (GDScript)
├── scenarios.json5       # Senaryo verileri
├── icon.svg              # Proje ikonu
└── readme.md             # Bu dosya
```

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Godot Engine 4.3 veya üzeri
- 4 GB RAM
- 200 MB disk alanı

### Adımlar
1. [Godot Engine](https://godotengine.org/download) indirin
2. Proje dosyalarını bir klasöre kopyalayın
3. Godot'u açın ve "Import" ile `project.godot` dosyasını seçin
4. Play (▶️) butonuna tıklayın

### Alternatif
`project.godot` dosyasına çift tıklayarak doğrudan çalıştırabilirsiniz.

## 🎯 Oynanış

1. **Başlangıç**: E.D.A sistemi çevrimiçi olur
2. **Senaryolar**: 12 farklı kriz durumu ile karşılaşırsınız
3. **Kararlar**: Her senaryoda 3 seçenek arasından birini seçin
4. **Sonuçlar**: Kararlarınız değişkenleri etkiler
5. **Final**: Değişken durumunuza göre 4 farklı sondan biri

## 🎨 Tasarım Felsefesi

- **Minimalist UI**: Metne odaklanmış, temiz arayüz
- **Etik Odaklı**: Gerçek dünya AI etiği problemleri
- **Türkçe Yerelleştirme**: Tam Türkçe deneyim
- **Erişilebilirlik**: Basit kontroller, net metin

## 🔧 Geliştirme Notları

- Oyun 2D tabanlıdır, 3D gerektirmez
- JSON5 formatı yorumlar için kullanılmıştır
- Responsive tasarım (mobil uyumlu)
- Modüler senaryo sistemi (kolay genişletme)

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 🤝 Katkıda Bulunma

Yeni senaryolar, çeviriler veya iyileştirmeler için katkıda bulunabilirsiniz.

---

**E.D.A - Extended Deep Awareness**  
*"Geleceğin etiği, bugünün kararlarında gizli"*