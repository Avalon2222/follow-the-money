import folium

from src import analisis, peta


def test_format_nilai_mengikuti_satuan():
    assert peta.format_nilai(50.0, "persen") == "50,0 %"
    assert peta.format_nilai(2_500_000, "rupiah_per_orang") == "Rp 2,50 jt / orang"
    assert peta.format_nilai(3e12, "rupiah") == "Rp 3,0 T"


def test_skala_legenda_memendekkan_angka():
    assert peta.skala_legenda("persen") == (1.0, "%")
    assert peta.skala_legenda("rupiah_per_orang") == (1e6, "juta Rp per orang")
    assert peta.skala_legenda("rupiah") == (1e12, "triliun Rp")


def test_sematkan_properti_tidak_mengubah_geojson_asli(apbd_mini, penduduk_mini):
    lebar = analisis.tabel_lebar(apbd_mini, penduduk_mini)
    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "id": "11", "properties": {"kode_bps": "11", "provinsi": "A"}, "geometry": None},
        {"type": "Feature", "id": "99", "properties": {"kode_bps": "99", "provinsi": "Z"}, "geometry": None},
    ]}
    hasil = peta.sematkan_properti(geo, lebar, "kemandirian")
    assert "nilai" not in geo["features"][0]["properties"]
    assert hasil["features"][0]["properties"]["nilai"] == "40,0 %"
    assert hasil["features"][1]["properties"]["nilai"] == "tidak ada data"


def test_buat_peta_dengan_data_nyata_menghasilkan_folium_map(apbd, penduduk, geojson):
    lebar = analisis.tabel_lebar(apbd, penduduk)
    th = lebar[lebar["tahun"] == 2024]
    m = peta.buat_peta(geojson, th, "belanja_per_kapita", 2024)
    assert isinstance(m, folium.Map)
    html = m.get_root().render()
    assert "Belanja per Penduduk" in html
    assert "Papua Pegunungan" in html
