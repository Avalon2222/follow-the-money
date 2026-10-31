import importlib.util
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("unduh_djpk", AKAR / "scripts" / "unduh_djpk.py")
unduh_djpk = importlib.util.module_from_spec(spec)
sys.modules["unduh_djpk"] = unduh_djpk
spec.loader.exec_module(unduh_djpk)

CONTOH_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
<Worksheet ss:Name="Data APBD"><Table>
<Row><Cell><Data ss:Type="String">Akun</Data></Cell><Cell><Data ss:Type="String">Anggaran</Data></Cell><Cell><Data ss:Type="String">Realisasi</Data></Cell><Cell><Data ss:Type="String">Persentase</Data></Cell></Row>
<Row><Cell><Data ss:Type="String"> Pendapatan Daerah</Data></Cell><Cell><Data ss:Type="Number">1.5E+14</Data></Cell><Cell><Data ss:Type="Number">140000000000000</Data></Cell><Cell><Data ss:Type="String">93.33</Data></Cell></Row>
<Row><Cell><Data ss:Type="String"> Belanja Daerah</Data></Cell><Cell><Data ss:Type="Number">100</Data></Cell><Cell><Data ss:Type="Number">90</Data></Cell><Cell><Data ss:Type="String">90</Data></Cell></Row>
<Row><Cell><Data ss:Type="String"> Belanja Pegawai</Data></Cell><Cell><Data ss:Type="Number">60</Data></Cell><Cell><Data ss:Type="Number">55</Data></Cell><Cell><Data ss:Type="String">91</Data></Cell></Row>
<Row><Cell><Data ss:Type="String"> Belanja Pegawai</Data></Cell><Cell><Data ss:Type="Number">60</Data></Cell><Cell><Data ss:Type="Number">55</Data></Cell><Cell><Data ss:Type="String">91</Data></Cell></Row>
<Row><Cell><Data ss:Type="String"> Belanja Barang Jasa</Data></Cell><Cell><Data ss:Type="Number">40</Data></Cell><Cell><Data ss:Type="Number">35</Data></Cell><Cell><Data ss:Type="String">87</Data></Cell></Row>
<Row><Cell><Data ss:Type="String"> Belanja Barang dan Jasa</Data></Cell><Cell><Data ss:Type="Number">40</Data></Cell><Cell><Data ss:Type="Number">35</Data></Cell><Cell><Data ss:Type="String">87</Data></Cell></Row>
<Row><Cell><Data ss:Type="String"> Akun Aneh</Data></Cell><Cell><Data ss:Type="Number">1</Data></Cell><Cell><Data ss:Type="Number">1</Data></Cell><Cell><Data ss:Type="String">100</Data></Cell></Row>
</Table></Worksheet></Workbook>
"""


def test_baca_xml_mengabaikan_judul_dan_membaca_notasi_ilmiah(tmp_path):
    p = tmp_path / "contoh.xml"
    p.write_text(CONTOH_XML, encoding="utf-8")
    baris = unduh_djpk.baca_xml(p)
    assert baris[0] == ("Pendapatan Daerah", 1.5e14, 1.4e14)
    assert len(baris) == 7


def test_baca_xml_halaman_galat_dianggap_kosong(tmp_path):
    p = tmp_path / "galat.xml"
    p.write_text("<?xml version='1.0'?><Workbook><!DOCTYPE html><html></html>", encoding="utf-8")
    assert unduh_djpk.baca_xml(p) == []


def test_rapikan_membuang_ganda_menyamakan_alias_dan_melewati_akun_asing(tmp_path, capsys):
    p = tmp_path / "contoh.xml"
    p.write_text(CONTOH_XML, encoding="utf-8")
    hasil = unduh_djpk.rapikan(unduh_djpk.baca_xml(p), "32", 2024)
    akun = [h["akun"] for h in hasil]
    assert akun == ["Pendapatan Daerah", "Belanja Daerah", "Belanja Pegawai", "Belanja Barang dan Jasa"]
    assert all(h["provinsi"] == "Jawa Barat" and h["tahun"] == 2024 for h in hasil)
    barang = hasil[-1]
    assert barang["induk"] == "Belanja Daerah" and barang["tingkat"] == 2
    assert barang["anggaran"] == 40 and barang["realisasi"] == 35
    assert "Akun Aneh" in capsys.readouterr().err
