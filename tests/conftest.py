import sys
from pathlib import Path

import pandas as pd
import pytest

AKAR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AKAR))

from src import muat_data  # noqa: E402


@pytest.fixture(scope="session")
def apbd() -> pd.DataFrame:
    return muat_data.muat_apbd()


@pytest.fixture(scope="session")
def penduduk() -> pd.DataFrame:
    return muat_data.muat_penduduk()


@pytest.fixture(scope="session")
def geojson() -> dict:
    return muat_data.muat_geojson()


@pytest.fixture
def apbd_mini() -> pd.DataFrame:
    """Dua provinsi fiktif, satu tahun, angka bulat agar mudah dihitung."""
    baris = []

    def tambah(kode, prov, akun, induk, tingkat, anggaran, realisasi):
        baris.append(dict(kode_bps=kode, provinsi=prov, tahun=2024, akun=akun, induk=induk,
                          tingkat=tingkat, anggaran=anggaran, realisasi=realisasi))

    # Provinsi A: pendapatan 100, PAD 40, TKDD 50, lainnya 10; belanja 80 (pegawai 40, barang 20, modal 16, lainnya 4)
    tambah("11", "A", "Pendapatan Daerah", "", 1, 110, 100)
    tambah("11", "A", "PAD", "Pendapatan Daerah", 2, 45, 40)
    tambah("11", "A", "Pajak Daerah", "PAD", 3, 30, 30)
    tambah("11", "A", "Retribusi Daerah", "PAD", 3, 15, 10)
    tambah("11", "A", "TKDD", "Pendapatan Daerah", 2, 55, 50)
    tambah("11", "A", "Pendapatan Transfer Pemerintah Pusat", "TKDD", 3, 55, 50)
    tambah("11", "A", "Pendapatan Lainnya", "Pendapatan Daerah", 2, 10, 10)
    tambah("11", "A", "Pendapatan Hibah", "Pendapatan Lainnya", 3, 10, 10)
    tambah("11", "A", "Belanja Daerah", "", 1, 100, 80)
    tambah("11", "A", "Belanja Pegawai", "Belanja Daerah", 2, 50, 40)
    tambah("11", "A", "Belanja Barang dan Jasa", "Belanja Daerah", 2, 25, 20)
    tambah("11", "A", "Belanja Modal", "Belanja Daerah", 2, 20, 16)
    tambah("11", "A", "Belanja Lainnya", "Belanja Daerah", 2, 5, 4)
    tambah("11", "A", "Belanja Hibah", "Belanja Lainnya", 3, 5, 4)
    # Provinsi B: pendapatan 50 semuanya transfer, belanja 50 semuanya modal, penduduk 0 (uji pembagi nol)
    tambah("12", "B", "Pendapatan Daerah", "", 1, 50, 50)
    tambah("12", "B", "TKDD", "Pendapatan Daerah", 2, 50, 50)
    tambah("12", "B", "Pendapatan Transfer Pemerintah Pusat", "TKDD", 3, 50, 50)
    tambah("12", "B", "Belanja Daerah", "", 1, 50, 50)
    tambah("12", "B", "Belanja Modal", "Belanja Daerah", 2, 50, 50)
    return pd.DataFrame(baris)


@pytest.fixture
def penduduk_mini() -> pd.DataFrame:
    return pd.DataFrame({"kode_bps": ["11", "12"], "provinsi": ["A", "B"],
                         "luas_km2": [1000.0, 500.0], "penduduk_2025": [1_000_000, 0]})
