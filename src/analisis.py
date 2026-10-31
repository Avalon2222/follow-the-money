"""Perhitungan indikator fiskal per provinsi dari tabel APBD rapi."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.skema import PULAU, label

# Akun yang diangkat menjadi kolom pada tabel lebar
AKUN_KOLOM: dict[str, str] = {
    "Pendapatan Daerah": "pendapatan",
    "PAD": "pad",
    "TKDD": "tkdd",
    "Pendapatan Lainnya": "pendapatan_lainnya",
    "Pajak Daerah": "pajak",
    "Belanja Daerah": "belanja",
    "Belanja Pegawai": "belanja_pegawai",
    "Belanja Barang dan Jasa": "belanja_barang",
    "Belanja Modal": "belanja_modal",
    "Belanja Lainnya": "belanja_lainnya",
    "Sisa Lebih Perhitungan Anggaran Tahun Sebelumnya": "silpa",
}


@dataclass(frozen=True)
class Metrik:
    kunci: str
    nama: str
    satuan: str  # "rupiah" | "persen" | "rupiah_per_orang"
    keterangan: str
    skema_warna: str = "YlGnBu"


METRIK: dict[str, Metrik] = {
    m.kunci: m
    for m in [
        Metrik("belanja", "Total Belanja Daerah", "rupiah",
               "Seluruh belanja pemda (provinsi + kabupaten/kota) di provinsi tersebut.", "YlGnBu"),
        Metrik("pendapatan", "Total Pendapatan Daerah", "rupiah",
               "PAD + transfer dari pusat + pendapatan lainnya.", "YlGnBu"),
        Metrik("tkdd", "Transfer dari Pusat (TKD)", "rupiah",
               "Dana yang dikirim APBN ke daerah: DAU, DBH, DAK, Dana Desa, Otsus, dan lain-lain.", "PuBu"),
        Metrik("pad", "Pendapatan Asli Daerah", "rupiah",
               "Pajak daerah, retribusi, hasil BUMD, dan lain-lain PAD.", "BuGn"),
        Metrik("belanja_per_kapita", "Belanja per Penduduk", "rupiah_per_orang",
               "Total belanja daerah dibagi jumlah penduduk.", "YlOrRd"),
        Metrik("tkdd_per_kapita", "Transfer Pusat per Penduduk", "rupiah_per_orang",
               "Transfer dari pusat dibagi jumlah penduduk.", "PuRd"),
        Metrik("kemandirian", "Kemandirian Fiskal (PAD / Pendapatan)", "persen",
               "Semakin tinggi, semakin sedikit daerah bergantung pada kiriman pusat.", "Greens"),
        Metrik("ketergantungan", "Ketergantungan pada Pusat (TKD / Pendapatan)", "persen",
               "Porsi pendapatan yang berasal dari transfer pusat.", "Oranges"),
        Metrik("porsi_modal", "Porsi Belanja Modal", "persen",
               "Bagian belanja untuk aset jangka panjang: jalan, gedung, irigasi, alat.", "Blues"),
        Metrik("porsi_pegawai", "Porsi Belanja Pegawai", "persen",
               "Bagian belanja untuk gaji dan tunjangan aparatur.", "Reds"),
        Metrik("serapan_belanja", "Serapan Belanja (Realisasi / Anggaran)", "persen",
               "Seberapa besar anggaran belanja benar-benar terpakai.", "Purples"),
        Metrik("capaian_pendapatan", "Capaian Pendapatan (Realisasi / Target)", "persen",
               "Realisasi pendapatan dibanding target di APBD.", "GnBu"),
    ]
}


def tabel_lebar(apbd: pd.DataFrame, penduduk: pd.DataFrame, basis: str = "realisasi") -> pd.DataFrame:
    """Satu baris per (provinsi, tahun) dengan kolom indikator.

    basis: "realisasi" (default) atau "anggaran" untuk nilai pokok. Rasio
    serapan/capaian selalu memakai keduanya.
    """
    if basis not in ("realisasi", "anggaran"):
        raise ValueError("basis harus 'realisasi' atau 'anggaran'")
    inti = apbd[apbd["akun"].isin(AKUN_KOLOM)].copy()
    inti["kolom"] = inti["akun"].map(AKUN_KOLOM)
    lebar = inti.pivot_table(index=["kode_bps", "provinsi", "tahun"], columns="kolom",
                             values=basis, aggfunc="sum").reset_index()
    for kolom in AKUN_KOLOM.values():
        if kolom not in lebar:
            lebar[kolom] = 0.0
    lebar = lebar.fillna(0.0)

    # pasangan anggaran vs realisasi untuk rasio serapan
    pasang = apbd[apbd["akun"].isin(["Belanja Daerah", "Pendapatan Daerah"])]
    pasang = pasang.pivot_table(index=["kode_bps", "tahun"], columns="akun",
                                values=["anggaran", "realisasi"], aggfunc="sum")
    pasang.columns = [f"{a}_{'belanja' if b == 'Belanja Daerah' else 'pendapatan'}" for a, b in pasang.columns]
    lebar = lebar.merge(pasang.reset_index(), on=["kode_bps", "tahun"], how="left")

    lebar = lebar.merge(penduduk[["kode_bps", "penduduk_2025", "luas_km2"]], on="kode_bps", how="left")
    lebar = lebar.rename(columns={"penduduk_2025": "penduduk"})
    lebar["pulau"] = lebar["kode_bps"].map(PULAU)
    return tambah_rasio(lebar)


def tambah_rasio(lebar: pd.DataFrame) -> pd.DataFrame:
    """Menambahkan kolom rasio turunan; aman terhadap pembagi nol."""
    df = lebar.copy()

    def bagi(a: str, b: str, kali: float = 1.0) -> pd.Series:
        pembagi = df[b].where(df[b] != 0)
        return (df[a] / pembagi * kali).astype(float)

    df["belanja_per_kapita"] = bagi("belanja", "penduduk")
    df["pendapatan_per_kapita"] = bagi("pendapatan", "penduduk")
    df["tkdd_per_kapita"] = bagi("tkdd", "penduduk")
    df["kemandirian"] = bagi("pad", "pendapatan", 100)
    df["ketergantungan"] = bagi("tkdd", "pendapatan", 100)
    df["porsi_modal"] = bagi("belanja_modal", "belanja", 100)
    df["porsi_pegawai"] = bagi("belanja_pegawai", "belanja", 100)
    df["porsi_barang"] = bagi("belanja_barang", "belanja", 100)
    df["porsi_lainnya"] = bagi("belanja_lainnya", "belanja", 100)
    if "realisasi_belanja" in df:
        df["serapan_belanja"] = bagi("realisasi_belanja", "anggaran_belanja", 100)
        df["capaian_pendapatan"] = bagi("realisasi_pendapatan", "anggaran_pendapatan", 100)
    df["surplus"] = df["pendapatan"] - df["belanja"]
    return df


def tambah_pertumbuhan(lebar: pd.DataFrame, kolom: str = "belanja") -> pd.DataFrame:
    """Pertumbuhan tahunan (%) kolom tertentu per provinsi."""
    df = lebar.sort_values(["kode_bps", "tahun"]).copy()
    sebelumnya = df.groupby("kode_bps")[kolom].shift(1)
    df[f"pertumbuhan_{kolom}"] = (df[kolom] / sebelumnya.where(sebelumnya != 0) - 1) * 100
    return df


def ringkasan_nasional(lebar_tahun: pd.DataFrame) -> dict[str, float]:
    """Agregat seluruh provinsi untuk satu tahun."""
    total = lebar_tahun[["pendapatan", "belanja", "pad", "tkdd", "belanja_modal", "belanja_pegawai", "penduduk"]].sum()
    return {
        "pendapatan": float(total["pendapatan"]),
        "belanja": float(total["belanja"]),
        "pad": float(total["pad"]),
        "tkdd": float(total["tkdd"]),
        "ketergantungan": float(total["tkdd"] / total["pendapatan"] * 100) if total["pendapatan"] else float("nan"),
        "kemandirian": float(total["pad"] / total["pendapatan"] * 100) if total["pendapatan"] else float("nan"),
        "porsi_modal": float(total["belanja_modal"] / total["belanja"] * 100) if total["belanja"] else float("nan"),
        "porsi_pegawai": float(total["belanja_pegawai"] / total["belanja"] * 100) if total["belanja"] else float("nan"),
        "belanja_per_kapita": float(total["belanja"] / total["penduduk"]) if total["penduduk"] else float("nan"),
    }


def peringkat(lebar_tahun: pd.DataFrame, metrik: str, n: int | None = None, terbesar: bool = True) -> pd.DataFrame:
    """Mengurutkan provinsi menurut sebuah metrik dan memberi nomor peringkat."""
    df = lebar_tahun.dropna(subset=[metrik]).sort_values(metrik, ascending=not terbesar).copy()
    df["peringkat"] = range(1, len(df) + 1)
    return df.head(n) if n else df


def aliran_sankey(apbd: pd.DataFrame, kode_bps: str, tahun: int, basis: str = "realisasi") -> dict:
    """Simpul dan tautan untuk diagram Sankey: sumber pendapatan -> kas daerah -> jenis belanja.

    Mengembalikan dict {"label": [...], "sumber": [...], "tujuan": [...], "nilai": [...]}.
    """
    df = apbd[(apbd["kode_bps"] == kode_bps) & (apbd["tahun"] == tahun)]
    nilai = dict(zip(df["akun"], df[basis]))
    kas = "Kas Daerah"
    label_simpul: list[str] = []
    indeks: dict[str, int] = {}

    def simpul(nama: str) -> int:
        if nama not in indeks:
            indeks[nama] = len(label_simpul)
            label_simpul.append(nama)
        return indeks[nama]

    sumber, tujuan, jumlah = [], [], []

    def tautan(a: str, b: str, v: float) -> None:
        if v and v > 0:
            sumber.append(simpul(a))
            tujuan.append(simpul(b))
            jumlah.append(float(v))

    # pendapatan: rincian -> jenis -> kas
    for jenis in ("PAD", "TKDD", "Pendapatan Lainnya"):
        rincian = df[(df["induk"] == jenis) & (df["tingkat"] == 3)]
        for _, r in rincian.iterrows():
            tautan(label(r["akun"]), label(jenis), r[basis])
        tautan(label(jenis), kas, nilai.get(jenis, 0))

    # belanja: kas -> jenis -> rincian (untuk belanja lainnya)
    for jenis in ("Belanja Pegawai", "Belanja Barang dan Jasa", "Belanja Modal", "Belanja Lainnya"):
        tautan(kas, jenis, nilai.get(jenis, 0))
    rincian = df[(df["induk"] == "Belanja Lainnya") & (df["tingkat"] == 3)]
    for _, r in rincian.iterrows():
        tautan("Belanja Lainnya", label(r["akun"]), r[basis])

    return {"label": label_simpul, "sumber": sumber, "tujuan": tujuan, "nilai": jumlah}


def komposisi_belanja(lebar_tahun: pd.DataFrame) -> pd.DataFrame:
    """Tabel panjang porsi belanja (%) per jenis untuk grafik batang bertumpuk."""
    kolom = {
        "porsi_pegawai": "Pegawai",
        "porsi_barang": "Barang & Jasa",
        "porsi_modal": "Modal",
        "porsi_lainnya": "Lainnya (bagi hasil, bankeu, hibah, bansos)",
    }
    panjang = lebar_tahun.melt(id_vars=["kode_bps", "provinsi", "pulau"], value_vars=list(kolom),
                               var_name="jenis", value_name="porsi")
    panjang["jenis"] = panjang["jenis"].map(kolom)
    return panjang


def agregat_pulau(lebar_tahun: pd.DataFrame) -> pd.DataFrame:
    """Jumlah pendapatan, belanja, TKD, dan penduduk per pulau besar beserta rasionya."""
    kolom = ["pendapatan", "belanja", "pad", "tkdd", "belanja_modal", "belanja_pegawai",
             "belanja_barang", "belanja_lainnya", "penduduk"]
    g = lebar_tahun.groupby("pulau", as_index=False)[kolom].sum()
    return tambah_rasio(g)
