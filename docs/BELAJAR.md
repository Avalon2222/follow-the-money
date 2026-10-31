# 🎓 Belajar dari Follow the Money

Bahan bacaan santai untuk memahami apa yang ditampilkan dasbor ini dan bagaimana ia dibangun.
Tidak perlu latar belakang ekonomi. Kalau sudah paham satu bagian, lompat saja ke bagian berikutnya.

---

## 1. APBD dalam bahasa warung kopi

Bayangkan sebuah provinsi sebagai rumah tangga besar.

- **Pendapatan** adalah uang yang masuk ke dompet. Ada yang dicari sendiri (**PAD**: pajak kendaraan, pajak
  hotel, retribusi parkir, laba BUMD) dan ada yang **dikirim orang tua di Jakarta** (**TKD**, Transfer ke Daerah:
  DAU, DBH, DAK, Dana Desa, dana otonomi khusus).
- **Belanja** adalah uang yang keluar. Dibagi empat: **pegawai** (gaji dan tunjangan), **barang dan jasa**
  (listrik kantor, ATK, perjalanan dinas, honor), **modal** (jalan, jembatan, gedung sekolah, alat kesehatan),
  dan **lainnya** (bagi hasil ke kabupaten/kota, bantuan keuangan, hibah, bantuan sosial).
- **Pembiayaan** adalah cara menutup selisih. Kalau belanja lebih besar dari pendapatan, pakai **SiLPA**
  (sisa uang tahun lalu) atau pinjaman.

Dua angka selalu muncul berpasangan: **anggaran** (rencana yang disahkan DPRD) dan **realisasi** (yang
benar-benar terjadi). Rasio keduanya disebut **serapan**. Serapan belanja 85 % berarti 15 % rencana tidak
jadi dibelanjakan; bisa karena hemat, bisa karena proyek tidak jalan.

> 💡 Angka di dasbor ini adalah **agregat seluruh pemda** dalam satu provinsi: pemprov ditambah semua
> kabupaten/kota. Jadi "Belanja Jawa Barat" bukan belanja Gedung Sate saja, melainkan Gedung Sate + 27 kabupaten/kota.

---

## 2. Tiga indikator yang bikin cerita

### Kemandirian fiskal = PAD ÷ Pendapatan

Berapa bagian dompet yang diisi sendiri. DKI Jakarta di atas 70 %: pajak kendaraan dan hotel di ibu kota cukup
untuk hidup tanpa kiriman pusat. Banyak provinsi di luar Jawa di bawah 15 %: tanpa transfer, roda pemerintahan
berhenti. Angka nasional sekitar 30 %.

### Belanja per penduduk = Belanja ÷ Penduduk

Membagi dengan penduduk mengubah peta sepenuhnya. Pada total belanja, Jawa Barat, Jawa Timur, dan Jawa Tengah
paling gelap karena penduduknya 130 juta. Pada belanja per penduduk, giliran Kalimantan Timur, Kalimantan Utara,
dan provinsi-provinsi di Papua yang paling gelap: penduduk sedikit, dana bagi hasil migas/tambang besar,
atau dana otonomi khusus besar.

Mana yang benar? Keduanya. Total menjawab "ke mana uang paling banyak dikirim", per kapita menjawab
"berapa uang yang tersedia untuk tiap warga".

### Porsi belanja modal = Belanja Modal ÷ Belanja

Berapa bagian uang yang menjadi aset tahan lama. Angka nasional sekitar 16 %. Belanja pegawai biasanya
sekitar 30 %. Provinsi dengan porsi modal tinggi dan pegawai rendah bukan otomatis lebih baik, tetapi
rasio ini adalah titik awal yang bagus untuk bertanya "uangnya jadi apa?".

---

## 3. Membaca choropleth tanpa tertipu

Choropleth adalah peta yang mewarnai wilayah menurut satu angka. Tiga jebakan klasik:

1. **Luas ≠ penting.** Kalimantan Tengah 4 kali luas Jawa Barat, tetapi belanjanya seperempat. Mata kita
   otomatis menganggap bidang besar sebagai nilai besar. Selalu cek legenda.
2. **Kelas warna.** Folium membagi rentang nilai menjadi beberapa kelas (*bins*). Satu provinsi ekstrem dapat
   membuat kelas teratas berisi dirinya sendiri dan semua yang lain tampak seragam. Coba indikator
   kemandirian fiskal: Jakarta sendirian di kelas tertinggi.
3. **Warna sekuensial vs divergen.** Untuk nilai yang semakin besar semakin "banyak", pakai satu gradasi
   (terang → gelap). Skema divergen (merah ↔ biru) hanya untuk nilai yang punya titik tengah bermakna, misalnya
   surplus/defisit.

Secara teknis, choropleth di proyek ini dibuat dengan `folium.Choropleth`, yang menggabungkan GeoJSON dan
DataFrame lewat satu kunci bersama, yaitu `kode_bps`. Kuncinya harus **persis sama** di kedua sisi; itulah
sebabnya `src/skema.py` memetakan kode urut DJPK (01–38) ke kode BPS (11–96) sebelum data dipakai.

---

## 4. Dari tabel panjang ke diagram Sankey

Data mentah berbentuk **tabel panjang**: satu baris per (provinsi, tahun, akun). Setiap akun punya `induk`
dan `tingkat`, misalnya `Pajak Daerah` (tingkat 3) → `PAD` (tingkat 2) → `Pendapatan Daerah` (tingkat 1).

Diagram Sankey hanya butuh tiga daftar: `sumber`, `tujuan`, `nilai`. Fungsi `aliran_sankey()` di
`src/analisis.py` membangunnya dengan dua langkah:

1. Untuk setiap rincian pendapatan, buat tautan **rincian → jenis**, lalu **jenis → Kas Daerah**.
2. Untuk setiap jenis belanja, buat tautan **Kas Daerah → jenis**, dan untuk Belanja Lainnya, **jenis → rincian**.

Tautan bernilai nol dibuang supaya diagram tidak dipenuhi pita tipis. Tes `test_sankey_seimbang_dan_tanpa_tautan_nol`
memastikan jumlah pita yang masuk ke Kas Daerah sama dengan total pendapatan, dan yang keluar sama dengan total belanja.

---

## 5. Tabel panjang vs tabel lebar

| Bentuk | Contoh | Enak untuk |
|---|---|---|
| Panjang | `provinsi, tahun, akun, nilai` | menyimpan, memfilter, menggabungkan sumber baru |
| Lebar | `provinsi, tahun, pad, tkdd, belanja, ...` | menghitung rasio antar kolom, membuat grafik |

`tabel_lebar()` mengubah panjang → lebar dengan `pivot_table`, lalu `tambah_rasio()` menghitung semua indikator.
Pembagian selalu memakai `where(pembagi != 0)` agar hasilnya `NaN`, bukan error, ketika penduduk atau pendapatan
kosong. `NaN` kemudian ditampilkan sebagai "-" oleh `src/format.py`.

---

## 6. Mengapa skala logaritmik pada scatter

Belanja per penduduk berkisar dari Rp 2 juta sampai Rp 20 juta lebih. Pada skala biasa, 30 provinsi menumpuk
di kiri dan 5 provinsi terpencar di kanan. Skala log memberi jarak yang sama untuk setiap **kelipatan**
(2 → 4 → 8 juta), sehingga perbedaan 2 vs 3 juta terlihat sama jelasnya dengan 10 vs 15 juta.

Ukuran lingkaran dipetakan ke **luas**, bukan jari-jari (perilaku bawaan `size` di Plotly Express), supaya
provinsi berpenduduk dua kali lipat terlihat dua kali lebih besar, bukan empat kali.

---

## 7. Dari portal pemerintah ke CSV yang bisa dipercaya

Portal SIKD DJPK tidak menyediakan API resmi, tetapi tombol ekspor di halamannya memanggil satu URL dengan
parameter tahun, provinsi, dan periode. `scripts/unduh_djpk.py` memanggil URL itu 38 × 3 kali, menyimpan setiap
jawaban ke cache, lalu merapikannya. Tiga kejutan yang ditemui saat merapikan, dan bagaimana ditangani:

| Kejutan | Penanganan |
|---|---|
| Belanja Pegawai/Barang/Modal muncul dua kali (jenis dan rincian dengan angka sama) | buang baris yang namanya sama dengan baris sebelumnya |
| "Belanja Barang Jasa" vs "Belanja Barang dan Jasa" | tabel alias di `skema.py` |
| Provinsi baru di Papua belum ada pada 2022, portal mengembalikan halaman HTML | tangkap `ParseError`, anggap tidak ada data |

Setiap penanganan itu punya tes di `tests/test_unduh.py`. Begitulah data publik yang berantakan diubah menjadi
dataset yang bisa dipakai ulang: bukan dengan menyunting tangan, tetapi dengan skrip yang bisa dijalankan lagi.

---

## 8. Pertanyaan untuk direnungkan

- Kalau dua provinsi punya belanja per penduduk sama, tetapi satu dari PAD dan satu dari transfer, apa bedanya bagi warganya?
- Serapan belanja 100 % selalu baik? Bagaimana dengan 110 % pada pendapatan?
- Transfer antar daerah tercatat dua kali dalam agregat. Berapa besar efeknya pada total pendapatan nasional di dasbor ini? (Petunjuk: tab Data & Sumber, akun "Transfer Antar Daerah".)

Lanjut ke [`LATIHAN.md`](LATIHAN.md) untuk mencoba sendiri.
