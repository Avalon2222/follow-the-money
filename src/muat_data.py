"""Memuat dataset yang dibundel di folder data/."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.skema import ALIAS_AKUN, NAMA_PROVINSI, PULAU

AKAR = Path(__file__).resolve().parents[1]
FOLDER_DATA = AKAR / "data"


def muat_apbd(path: Path | None = None) -> pd.DataFrame:
    """Tabel rapi APBD: satu baris per (provinsi, tahun, akun)."""
    path = path or FOLDER_DATA / "apbd_provinsi.csv"
    df = pd.read_csv(path, dtype={"kode_bps": str, "induk": str})
    # Sama seperti muat_penduduk: kode " 11" harus tetap cocok dengan skema pulau dan GeoJSON.
    df["kode_bps"] = df["kode_bps"].str.strip()
    # Nama akun dirapikan seperti di skrip unduh: spasi berlebih dan ejaan lain DJPK
    # ("Belanja Barang Jasa") membuat akun itu tidak terbaca di tabel lebar maupun Sankey.
    for kolom in ("akun", "induk"):
        df[kolom] = df[kolom].fillna("").astype(str).str.strip().replace(ALIAS_AKUN)
    # Baris tanpa tahun/tingkat (sel kosong di CSV) tidak bisa dipetakan; buang daripada astype(int) gagal.
    for kolom in ("tahun", "tingkat"):
        df[kolom] = pd.to_numeric(df[kolom], errors="coerce")
    # Tahun/tingkat pecahan (2024.5) juga dibuang; astype(int) diam-diam memotongnya jadi 2024.
    utuh = (df["tahun"] % 1 == 0) & (df["tingkat"] % 1 == 0)
    df = df[utuh].dropna(subset=["tahun", "tingkat"]).copy()
    # Sel rupiah berisi teks (mis. "-" untuk kosong) membuat kolom jadi object, lalu pivot_table
    # menyambung teks alih-alih menjumlahkan; jadikan angka, sel rusak jadi NaN.
    # inf (sel rusak) juga jadi NaN; kalau lolos, total provinsi dan semua rasionya ikut tak hingga.
    for kolom in ("anggaran", "realisasi"):
        angka = pd.to_numeric(df[kolom], errors="coerce")
        df[kolom] = angka.where(angka.abs() != float("inf"))
    df["tahun"] = df["tahun"].astype(int)
    df["tingkat"] = df["tingkat"].astype(int)
    df["pulau"] = df["kode_bps"].map(PULAU)
    return df


def muat_penduduk(path: Path | None = None) -> pd.DataFrame:
    """Penduduk (proyeksi pertengahan 2025) dan luas wilayah per provinsi."""
    path = path or FOLDER_DATA / "penduduk_provinsi.csv"
    df = pd.read_csv(path, dtype={"kode_bps": str})
    # Penduduk kosong dibiarkan NaN (rasio per kapita jadi "-"), tidak membuat astype gagal.
    penduduk = pd.to_numeric(df["penduduk_2025"], errors="coerce")
    # inf lolos dari notna() lalu membuat astype("int64") gagal; anggap kosong saja.
    # Penduduk negatif juga mustahil; kalau lolos, belanja per kapita ikut negatif.
    penduduk = penduduk.where((penduduk.abs() != float("inf")) & (penduduk >= 0))
    df["penduduk_2025"] = penduduk.astype("int64") if penduduk.notna().all() else penduduk
    df["kode_bps"] = df["kode_bps"].str.strip()
    return df


def muat_geojson(path: Path | None = None) -> dict:
    """GeoJSON batas 38 provinsi, properti: kode_bps dan provinsi."""
    path = path or FOLDER_DATA / "provinsi.geojson"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    # kode_bps berupa angka (11) atau berspasi (" 11") tidak cocok dengan kode teks di tabel APBD,
    # sehingga seluruh peta jadi abu-abu "tidak ada data". Samakan jadi teks rapi.
    for fitur in data.get("features", []):
        prop = fitur.get("properties") or {}
        kode = prop.get("kode_bps")
        if isinstance(kode, float) and kode.is_integer():
            kode = int(kode)
        if kode is not None:
            prop["kode_bps"] = str(kode).strip()
    return data


def muat_sumber(path: Path | None = None) -> str:
    """Isi data/SUMBER_DATA.md sebagai teks."""
    path = path or FOLDER_DATA / "SUMBER_DATA.md"
    return path.read_text(encoding="utf-8")


def periksa_konsistensi(apbd: pd.DataFrame, penduduk: pd.DataFrame, geojson: dict) -> list[str]:
    """Mengembalikan daftar masalah (kosong jika semua kunci cocok)."""
    masalah: list[str] = []
    # Kode kosong (NaN) dilaporkan sendiri; kalau ikut di-sorted bersama teks, fungsi ini malah TypeError.
    for nama, df in (("APBD", apbd), ("penduduk", penduduk)):
        if df["kode_bps"].isna().any():
            masalah.append(f"{nama}: {int(df['kode_bps'].isna().sum())} baris tanpa kode_bps")
    kode_apbd = set(apbd["kode_bps"].dropna())
    kode_pend = set(penduduk["kode_bps"].dropna())
    # Fitur tanpa properti kode_bps dilaporkan, bukan membuat seluruh pemeriksaan KeyError.
    kode_geo_semua = [(f.get("properties") or {}).get("kode_bps") for f in geojson["features"]]
    if None in kode_geo_semua:
        masalah.append(f"geojson: {kode_geo_semua.count(None)} fitur tanpa kode_bps")
    kode_geo = {k for k in kode_geo_semua if k is not None}
    kode_skema = set(NAMA_PROVINSI)
    if kode_apbd - kode_skema:
        masalah.append(f"kode APBD di luar skema: {sorted(kode_apbd - kode_skema)}")
    if kode_pend != kode_skema:
        masalah.append(f"penduduk tidak lengkap/berlebih: {sorted(kode_pend ^ kode_skema)}")
    if kode_geo != kode_skema:
        masalah.append(f"geojson tidak lengkap/berlebih: {sorted(kode_geo ^ kode_skema)}")
    return masalah
