"""Mengunduh dan merapikan data APBD per provinsi dari Portal Data SIKD, DJPK Kemenkeu.

Portal: https://djpk.kemenkeu.go.id/portal/data/apbd
Setiap kombinasi (tahun, provinsi) diekspor sebagai SpreadsheetML (XML) berisi
anggaran dan realisasi per akun, agregat seluruh pemda (provinsi + kabupaten/kota)
di provinsi tersebut. Skrip ini mengunduh 38 provinsi untuk beberapa tahun,
lalu menyusunnya menjadi satu CSV rapi di data/apbd_provinsi.csv.

Pemakaian:
    python scripts/unduh_djpk.py                  # unduh 2022-2024 ke cache lalu parse
    python scripts/unduh_djpk.py --tahun 2023 2024
    python scripts/unduh_djpk.py --cache folder   # pakai folder cache lain
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

AKAR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AKAR))

from src.skema import ALIAS_AKUN, KODE_DJPK_KE_BPS, NAMA_PROVINSI, STRUKTUR_AKUN  # noqa: E402

URL = (
    "https://djpk.kemenkeu.go.id/portal/csv_apbd"
    "?type=apbd&periode=12&tahun={tahun}&provinsi={kode}&pemda=--"
)
NS = "{urn:schemas-microsoft-com:office:spreadsheet}"
KOLOM = ["kode_bps", "provinsi", "tahun", "akun", "induk", "tingkat", "anggaran", "realisasi"]


def unduh(tahun: int, kode_djpk: str, cache: Path) -> Path:
    """Mengunduh satu ekspor ke cache (dilewati jika sudah ada)."""
    tujuan = cache / f"apbd_{tahun}_{kode_djpk}.xml"
    if tujuan.exists() and tujuan.stat().st_size > 1000:
        return tujuan
    url = URL.format(tahun=tahun, kode=kode_djpk)
    for percobaan in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                tujuan.write_bytes(r.read())
            return tujuan
        except Exception as e:  # noqa: BLE001
            print(f"  gagal ({e}), coba lagi...", file=sys.stderr)
            time.sleep(3 * (percobaan + 1))
    raise RuntimeError(f"Tidak bisa mengunduh {url}")


def baca_xml(path: Path) -> list[tuple[str, float, float]]:
    """Mengubah SpreadsheetML menjadi daftar (akun, anggaran, realisasi).

    Portal mengembalikan halaman galat (HTML) untuk kombinasi yang belum ada
    datanya, misalnya provinsi baru di Papua untuk tahun 2022. Kasus itu
    dikembalikan sebagai daftar kosong.
    """
    try:
        pohon = ET.parse(path)
    except ET.ParseError:
        print(f"  {path.name}: bukan XML utuh, dianggap tidak ada data", file=sys.stderr)
        return []
    baris = []
    for row in pohon.iter(NS + "Row"):
        sel = [(d.text or "").strip() for d in row.iter(NS + "Data")]
        if len(sel) < 3 or sel[0] == "Akun":
            continue
        baris.append((sel[0], float(sel[1] or 0), float(sel[2] or 0)))
    return baris


def rapikan(baris: list[tuple[str, float, float]], kode_bps: str, tahun: int) -> list[dict]:
    """Memberi tingkat dan induk pada setiap akun, membuang baris ganda."""
    hasil = []
    sebelumnya = None
    for akun, anggaran, realisasi in baris:
        akun = ALIAS_AKUN.get(akun, akun)
        if akun == sebelumnya:  # DJPK mengulang Belanja Pegawai/Barang/Modal dua kali
            continue
        sebelumnya = akun
        if akun not in STRUKTUR_AKUN:
            print(f"  akun tak dikenal dilewati: {akun!r}", file=sys.stderr)
            continue
        tingkat, induk = STRUKTUR_AKUN[akun]
        hasil.append(
            {
                "kode_bps": kode_bps,
                "provinsi": NAMA_PROVINSI[kode_bps],
                "tahun": tahun,
                "akun": akun,
                "induk": induk or "",
                "tingkat": tingkat,
                "anggaran": round(anggaran),
                "realisasi": round(realisasi),
            }
        )
    return hasil


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tahun", type=int, nargs="+", default=[2022, 2023, 2024])
    p.add_argument("--cache", type=Path, default=AKAR / ".cache_djpk")
    p.add_argument("--keluaran", type=Path, default=AKAR / "data" / "apbd_provinsi.csv")
    args = p.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)

    semua: list[dict] = []
    for tahun in args.tahun:
        for kode_djpk, kode_bps in KODE_DJPK_KE_BPS.items():
            print(f"{tahun} {NAMA_PROVINSI[kode_bps]}", flush=True)
            path = unduh(tahun, kode_djpk, args.cache)
            semua.extend(rapikan(baca_xml(path), kode_bps, tahun))
            time.sleep(0.3)

    with args.keluaran.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KOLOM)
        w.writeheader()
        w.writerows(semua)
    print(f"Tersimpan {len(semua)} baris ke {args.keluaran}")


if __name__ == "__main__":
    main()
