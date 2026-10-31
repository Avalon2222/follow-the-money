# ✍️ Latihan

Latihan bertingkat, dari membaca dasbor sampai mengubah kodenya. Setiap tingkat bisa dikerjakan terpisah.
Jawaban untuk tingkat 1 dan 2 bisa dicek sendiri lewat tab **Data & Sumber**.

---

## Tingkat 1: Membaca dasbor (tanpa kode)

1. Buka tab **Peta**, pilih *Total Belanja Daerah* lalu *Belanja per Penduduk* untuk tahun 2024.
   Sebutkan tiga provinsi yang berpindah dari kelas warna terang ke kelas gelap. Mengapa?
2. Pada indikator *Kemandirian Fiskal*, berapa provinsi yang berada di atas angka nasional? Pulau mana yang
   paling banyak di bawah 15 %?
3. Buka **Profil Provinsi** untuk Kalimantan Timur. Dari pita Sankey, perkirakan berapa persen pendapatannya
   yang datang dari pusat. Cocokkan dengan angka *Ketergantungan* di tab Data & Sumber.
4. Bandingkan komposisi belanja DKI Jakarta dan Papua Pegunungan. Mana yang porsi pegawainya lebih besar?
   Mana yang porsi modalnya lebih besar? Tulis satu kalimat dugaan mengapa.
5. Di tab **Tren**, pilih pertumbuhan *Belanja* 2023→2024. Provinsi mana yang tumbuh paling cepat?
   Apakah pertumbuhan itu terlihat juga pada *Transfer pusat*?

## Tingkat 2: Menelusuri data (pandas, tanpa mengubah aplikasi)

Jalankan dari folder proyek dengan `python` atau notebook.

```python
from src import muat_data, analisis
apbd = muat_data.muat_apbd()
penduduk = muat_data.muat_penduduk()
lebar = analisis.tabel_lebar(apbd, penduduk)
th = lebar[lebar["tahun"] == 2024]
```

6. Hitung total "Pendapatan Transfer Antar Daerah" seluruh provinsi 2024. Berapa persen dari total
   pendapatan daerah? Ini adalah perkiraan besar penghitungan ganda dalam agregat.
7. Buat tabel 10 provinsi dengan **serapan belanja** terendah 2024. Adakah pola pulau?
8. Hitung rasio **Belanja Modal per penduduk** (belum ada di tabel). Urutkan dan bandingkan dengan
   peringkat belanja per penduduk. Provinsi mana yang peringkatnya berbeda jauh?
9. Untuk setiap pulau, hitung median kemandirian fiskal (bukan rata-rata tertimbang seperti di dasbor).
   Mengapa hasilnya berbeda dengan tabel "Per pulau besar"?
10. Cari provinsi yang realisasi pendapatannya **melebihi** anggaran (capaian > 100 %) tiga tahun berturut-turut.

## Tingkat 3: Mengubah aplikasi

11. **Indikator baru.** Tambahkan `modal_per_kapita` (Belanja Modal ÷ Penduduk) ke `tambah_rasio()` di
    `src/analisis.py`, daftarkan sebagai `Metrik` di `METRIK`, lalu buka peta. Tulis satu tes di
    `tests/test_analisis.py` memakai fixture `apbd_mini` (nilai yang diharapkan untuk provinsi A adalah
    16 ÷ 1.000.000).
12. **Basemap.** Ganti `tiles` di `src/peta.py` ke penyedia lain yang gratis (misalnya `CartoDB positron`
    memerlukan kunci API; cari alternatif di dokumentasi Folium). Pastikan `tests/test_peta.py` masih lolos.
13. **Skema warna divergen.** Tambahkan indikator `surplus_per_kapita` dan beri skema warna divergen
    (`RdBu`) karena nilainya bisa negatif. Apa yang terjadi pada legenda Folium? Perlukah `bins` diatur manual?
14. **Tooltip.** Tambahkan porsi belanja modal ke tooltip peta (`sematkan_properti()` dan `GeoJsonTooltip`).
15. **Unduh ulang.** Jalankan `python scripts/unduh_djpk.py --tahun 2021` lalu periksa apakah nama akun
    2021 cocok dengan `STRUKTUR_AKUN`. Jika ada yang baru, tambahkan ke `skema.py` beserta tesnya.

## Tingkat 4: Proyek lanjutan

16. **Turun ke kabupaten/kota.** Portal DJPK menerima parameter `pemda`. Tulis skrip yang mengunduh semua
    pemda di satu provinsi, lalu buat peta kabupaten/kota untuk provinsi itu (GeoJSON kabupaten tersedia
    di repositori yang sama dengan sumber batas provinsi).
17. **Hubungkan dengan hasil.** Gabungkan belanja per penduduk dengan indikator BPS seperti Indeks Pembangunan
    Manusia atau tingkat kemiskinan per provinsi. Buat scatter dan tulis dua paragraf: apa yang terlihat,
    dan mengapa korelasi di sini belum berarti sebab-akibat.
18. **Pisahkan pemprov dan kab/kota.** Unduh APBD pemprov saja (`pemda=00`) dan hitung berapa persen belanja
    provinsi yang dikelola pemprov vs kabupaten/kota. Provinsi mana yang paling "terpusat" di pemprov?

---

### Petunjuk umum

- Semua fungsi analisis menerima dan mengembalikan DataFrame pandas biasa; coba dulu di notebook sebelum
  memasukkannya ke `app.py`.
- `pytest -q` seharusnya tetap hijau setelah setiap perubahan. Kalau tes gagal, baca pesan `assert`-nya:
  tes di proyek ini ditulis agar pesannya menjelaskan apa yang salah.
- Angka di README (misalnya "sekitar 30 %") adalah pembulatan untuk 2024; jika data diperbarui, perbarui juga kalimatnya.
