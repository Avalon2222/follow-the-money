"""Memuat dataset yang dibundel di folder data/."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.skema import NAMA_PROVINSI, PULAU

AKAR = Path(__file__).resolve().parents[1]
FOLDER_DATA = AKAR / "data"


def muat_apbd(path: Path | None = None) -> pd.DataFrame:
    """Tabel rapi APBD: satu baris per (provinsi, tahun, akun)."""
    path = path or FOLDER_DATA / "apbd_provinsi.csv"
    df = pd.read_csv(path, dtype={"kode_bps": str, "induk": str})
    # Sama seperti muat_penduduk: kode " 11" harus tetap cocok dengan skema pulau dan GeoJSON.
    df["kode_bps"] = df["kode_bps"].str.strip()
    df["induk"] = df["induk"].fillna("")
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
    df["penduduk_2025"] = penduduk.astype("int64") if penduduk.notna().all() else penduduk
    df["kode_bps"] = df["kode_bps"].str.strip()
    return df


def muat_geojson(path: Path | None = None) -> dict:
    """GeoJSON batas 38 provinsi, properti: kode_bps dan provinsi."""
    path = path or FOLDER_DATA / "provinsi.geojson"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def muat_sumber(path: Path | None = None) -> str:
    """Isi data/SUMBER_DATA.md sebagai teks."""
    path = path or FOLDER_DATA / "SUMBER_DATA.md"
    return path.read_text(encoding="utf-8")


def periksa_konsistensi(apbd: pd.DataFrame, penduduk: pd.DataFrame, geojson: dict) -> list[str]:
    """Mengembalikan daftar masalah (kosong jika semua kunci cocok)."""
    masalah: list[str] = []
    kode_apbd = set(apbd["kode_bps"])
    kode_pend = set(penduduk["kode_bps"])
    kode_geo = {f["properties"]["kode_bps"] for f in geojson["features"]}
    kode_skema = set(NAMA_PROVINSI)
    if kode_apbd - kode_skema:
        masalah.append(f"kode APBD di luar skema: {sorted(kode_apbd - kode_skema)}")
    if kode_pend != kode_skema:
        masalah.append(f"penduduk tidak lengkap/berlebih: {sorted(kode_pend ^ kode_skema)}")
    if kode_geo != kode_skema:
        masalah.append(f"geojson tidak lengkap/berlebih: {sorted(kode_geo ^ kode_skema)}")
    return masalah
