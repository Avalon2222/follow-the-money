# Sumber Data

Seluruh data dalam folder ini berasal dari sumber publik dan dapat diunduh ulang
dengan skrip `scripts/unduh_djpk.py`. Angka dalam rupiah penuh (bukan ribuan).

## 1. `apbd_provinsi.csv` — APBD per provinsi, 2022–2024

| Hal | Keterangan |
|---|---|
| Sumber | Portal Data SIKD, Direktorat Jenderal Perimbangan Keuangan (DJPK), Kementerian Keuangan: <https://djpk.kemenkeu.go.id/portal/data/apbd> |
| Titik akses | `https://djpk.kemenkeu.go.id/portal/csv_apbd?type=apbd&periode=12&tahun={tahun}&provinsi={kode}&pemda=--` |
| Cakupan | 38 provinsi; tahun 2022 (34 provinsi), 2023 dan 2024 (38 provinsi). Periode 12 = realisasi sampai Desember |
| Satuan wilayah | **Agregat seluruh pemerintah daerah** dalam satu provinsi: pemprov + semua kabupaten/kota. Bukan hanya APBD pemprov |
| Kolom | `kode_bps`, `provinsi`, `tahun`, `akun`, `induk`, `tingkat` (1 kelompok, 2 jenis, 3 rincian), `anggaran`, `realisasi` |
| Diunduh | 1 November 2026 |

Catatan pengolahan:

- Portal mengulang akun Belanja Pegawai, Belanja Barang dan Jasa, dan Belanja Modal dua kali (jenis dan rincian yang sama); baris ganda dibuang.
- Ejaan "Belanja Barang Jasa" pada sebagian ekspor disamakan menjadi "Belanja Barang dan Jasa".
- Kode urut DJPK (01–38) dipetakan ke kode wilayah BPS/Kemendagri (11–96) agar bisa digabung dengan peta dan data penduduk. Pemetaannya ada di `src/skema.py`.
- Empat provinsi baru di Papua (Papua Selatan, Papua Tengah, Papua Pegunungan, Papua Barat Daya) belum memiliki APBD pada 2022; angka Papua dan Papua Barat 2022 masih mencakup wilayah induk sebelum pemekaran.
- "Pendapatan Transfer Antar Daerah" sebagian besar adalah dana bagi hasil dan bantuan keuangan dari pemprov ke kabupaten/kota di provinsi yang sama. Karena agregat mencakup keduanya, komponen ini terhitung di sisi penerimaan kabupaten/kota sekaligus di sisi belanja pemprov.

## 2. `penduduk_provinsi.csv` — penduduk dan luas wilayah

| Hal | Keterangan |
|---|---|
| Sumber angka | Badan Pusat Statistik (BPS), proyeksi penduduk pertengahan tahun 2025 dan luas wilayah menurut provinsi |
| Diambil melalui | Tabel "Provinces of Indonesia" di Wikipedia bahasa Inggris, yang mengutip BPS: <https://en.wikipedia.org/wiki/Provinces_of_Indonesia> (diakses 1 November 2026) |
| Kolom | `kode_bps`, `provinsi`, `luas_km2`, `penduduk_2025` |

Penduduk 2025 dipakai sebagai pembagi untuk ketiga tahun APBD agar perbandingan antar provinsi tetap sederhana. Dampaknya pada nilai per kapita 2022–2023 kecil (pertumbuhan penduduk sekitar 1 % per tahun), tetapi perlu diingat saat membaca angka.

## 3. `provinsi.geojson` — batas 38 provinsi

| Hal | Keterangan |
|---|---|
| Sumber | *Indonesia GeoJSON & TopoJSON Maps (38 Provinces)* oleh Deny Herianto, lisensi data CC BY 4.0: <https://github.com/denyherianto/indonesia-geojson-topojson-maps-with-38-provinces> |
| Pengolahan | Properti diganti menjadi `kode_bps` dan `provinsi`; koordinat dibulatkan ke 4 angka desimal (sekitar 11 m) untuk memperkecil ukuran berkas |

## Penafian

Proyek ini bersifat edukatif dan merupakan portofolio pribadi. Angka ditampilkan apa adanya dari
sumber publik di atas dan dapat berbeda dari laporan keuangan daerah yang telah diaudit BPK.
Proyek ini tidak berafiliasi dengan Kementerian Keuangan, BPS, maupun pemerintah daerah mana pun.
