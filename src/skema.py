"""Skema tetap: kode provinsi dan struktur akun APBD (format SIKD/DJPK)."""
from __future__ import annotations

# Kode urut yang dipakai Portal DJPK -> kode wilayah BPS/Kemendagri
KODE_DJPK_KE_BPS: dict[str, str] = {
    "01": "11", "02": "12", "03": "13", "04": "14", "05": "15", "06": "16", "07": "17",
    "08": "18", "09": "31", "10": "32", "11": "33", "12": "34", "13": "35", "14": "61",
    "15": "62", "16": "63", "17": "64", "18": "71", "19": "72", "20": "73", "21": "74",
    "22": "51", "23": "52", "24": "53", "25": "81", "26": "91", "27": "82", "28": "36",
    "29": "19", "30": "75", "31": "21", "32": "92", "33": "76", "34": "65", "35": "93",
    "36": "94", "37": "95", "38": "96",
}

NAMA_PROVINSI: dict[str, str] = {
    "11": "Aceh", "12": "Sumatera Utara", "13": "Sumatera Barat", "14": "Riau", "15": "Jambi",
    "16": "Sumatera Selatan", "17": "Bengkulu", "18": "Lampung", "19": "Kepulauan Bangka Belitung",
    "21": "Kepulauan Riau", "31": "DKI Jakarta", "32": "Jawa Barat", "33": "Jawa Tengah",
    "34": "Daerah Istimewa Yogyakarta", "35": "Jawa Timur", "36": "Banten", "51": "Bali",
    "52": "Nusa Tenggara Barat", "53": "Nusa Tenggara Timur", "61": "Kalimantan Barat",
    "62": "Kalimantan Tengah", "63": "Kalimantan Selatan", "64": "Kalimantan Timur",
    "65": "Kalimantan Utara", "71": "Sulawesi Utara", "72": "Sulawesi Tengah", "73": "Sulawesi Selatan",
    "74": "Sulawesi Tenggara", "75": "Gorontalo", "76": "Sulawesi Barat", "81": "Maluku",
    "82": "Maluku Utara", "91": "Papua", "92": "Papua Barat", "93": "Papua Selatan",
    "94": "Papua Tengah", "95": "Papua Pegunungan", "96": "Papua Barat Daya",
}

PULAU: dict[str, str] = {
    **{k: "Sumatera" for k in ["11", "12", "13", "14", "15", "16", "17", "18", "19", "21"]},
    **{k: "Jawa" for k in ["31", "32", "33", "34", "35", "36"]},
    **{k: "Bali & Nusa Tenggara" for k in ["51", "52", "53"]},
    **{k: "Kalimantan" for k in ["61", "62", "63", "64", "65"]},
    **{k: "Sulawesi" for k in ["71", "72", "73", "74", "75", "76"]},
    **{k: "Maluku" for k in ["81", "82"]},
    **{k: "Papua" for k in ["91", "92", "93", "94", "95", "96"]},
}

# akun -> (tingkat, induk). Tingkat 1 = kelompok besar, 2 = jenis, 3 = rincian.
STRUKTUR_AKUN: dict[str, tuple[int, str | None]] = {
    "Pendapatan Daerah": (1, None),
    "PAD": (2, "Pendapatan Daerah"),
    "Pajak Daerah": (3, "PAD"),
    "Retribusi Daerah": (3, "PAD"),
    "Hasil Pengelolaan Kekayaan Daerah yang Dipisahkan": (3, "PAD"),
    "Lain-Lain PAD yang Sah": (3, "PAD"),
    "TKDD": (2, "Pendapatan Daerah"),
    "Pendapatan Transfer Pemerintah Pusat": (3, "TKDD"),
    "Pendapatan Lainnya": (2, "Pendapatan Daerah"),
    "Pendapatan Hibah": (3, "Pendapatan Lainnya"),
    "Dana Darurat": (3, "Pendapatan Lainnya"),
    "Lain-lain Pendapatan Sesuai dengan Ketentuan Peraturan Perundang-Undangan": (3, "Pendapatan Lainnya"),
    "Pendapatan Transfer Antar Daerah": (3, "Pendapatan Lainnya"),
    "Belanja Daerah": (1, None),
    "Belanja Pegawai": (2, "Belanja Daerah"),
    "Belanja Barang dan Jasa": (2, "Belanja Daerah"),
    "Belanja Modal": (2, "Belanja Daerah"),
    "Belanja Lainnya": (2, "Belanja Daerah"),
    "Belanja Bagi Hasil": (3, "Belanja Lainnya"),
    "Belanja Bantuan Keuangan": (3, "Belanja Lainnya"),
    "Belanja Bunga": (3, "Belanja Lainnya"),
    "Belanja Subsidi": (3, "Belanja Lainnya"),
    "Belanja Hibah": (3, "Belanja Lainnya"),
    "Belanja Bantuan Sosial": (3, "Belanja Lainnya"),
    "Belanja Tidak Terduga": (3, "Belanja Lainnya"),
    "Pembiayaan Daerah": (1, None),
    "Penerimaan Pembiayaan Daerah": (2, "Pembiayaan Daerah"),
    "Sisa Lebih Perhitungan Anggaran Tahun Sebelumnya": (3, "Penerimaan Pembiayaan Daerah"),
    "Pencairan Dana Cadangan": (3, "Penerimaan Pembiayaan Daerah"),
    "Penjualan Kekayaan Daerah yang Dipisahkan": (3, "Penerimaan Pembiayaan Daerah"),
    "Penerimaan Pinjaman Daerah": (3, "Penerimaan Pembiayaan Daerah"),
    "Penerimaan Kembali Pemberian Pinjaman Daerah": (3, "Penerimaan Pembiayaan Daerah"),
    "Penerimaan Pembiayaan Lainnya Sesuai dengan Ketentuan Peraturan Perundang-Undangan": (3, "Penerimaan Pembiayaan Daerah"),
    "Pengeluaran Pembiayaan Daerah": (2, "Pembiayaan Daerah"),
    "Pembentukan Dana Cadangan": (3, "Pengeluaran Pembiayaan Daerah"),
    "Penyertaan Modal Daerah": (3, "Pengeluaran Pembiayaan Daerah"),
    "Pembayaran Cicilan Pokok Utang yang Jatuh Tempo": (3, "Pengeluaran Pembiayaan Daerah"),
    "Pemberian Pinjaman Daerah": (3, "Pengeluaran Pembiayaan Daerah"),
    "Pengeluaran Pembiayaan Lainnya Sesuai dengan Ketentuan Peraturan Perundang-Undangan": (3, "Pengeluaran Pembiayaan Daerah"),
}

# Ejaan lain yang muncul di sebagian ekspor DJPK -> nama baku
ALIAS_AKUN: dict[str, str] = {
    "Belanja Barang Jasa": "Belanja Barang dan Jasa",
}

# Nama yang lebih ramah untuk tampilan
LABEL_AKUN: dict[str, str] = {
    "PAD": "Pendapatan Asli Daerah",
    "TKDD": "Transfer dari Pusat (TKD)",
    "Hasil Pengelolaan Kekayaan Daerah yang Dipisahkan": "Hasil Kekayaan Daerah (BUMD)",
    "Lain-Lain PAD yang Sah": "Lain-lain PAD",
    "Lain-lain Pendapatan Sesuai dengan Ketentuan Peraturan Perundang-Undangan": "Lain-lain Pendapatan",
    "Pendapatan Transfer Antar Daerah": "Transfer Antar Daerah",
    "Pendapatan Transfer Pemerintah Pusat": "Transfer Pemerintah Pusat",
    "Sisa Lebih Perhitungan Anggaran Tahun Sebelumnya": "SiLPA Tahun Sebelumnya",
    "Penerimaan Pembiayaan Lainnya Sesuai dengan Ketentuan Peraturan Perundang-Undangan": "Penerimaan Pembiayaan Lainnya",
    "Pengeluaran Pembiayaan Lainnya Sesuai dengan Ketentuan Peraturan Perundang-Undangan": "Pengeluaran Pembiayaan Lainnya",
    "Pembayaran Cicilan Pokok Utang yang Jatuh Tempo": "Cicilan Pokok Utang",
}


def label(akun: str) -> str:
    """Nama tampilan untuk sebuah akun."""
    return LABEL_AKUN.get(akun, akun)
