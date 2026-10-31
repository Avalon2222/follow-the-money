"""Peta choropleth Folium untuk indikator per provinsi."""
from __future__ import annotations

import copy

import folium
import pandas as pd

from src.analisis import METRIK
from src.format import orang, persen, rupiah

PUSAT_INDONESIA = (-2.5, 118.0)
BATAS_INDONESIA = [[-11.0, 94.5], [6.5, 141.5]]  # [[selatan, barat], [utara, timur]]


def format_nilai(nilai: float, satuan: str) -> str:
    """Memformat nilai sesuai jenis satuan metrik."""
    if satuan == "persen":
        return persen(nilai)
    if satuan == "rupiah_per_orang":
        return rupiah(nilai, 2) + " / orang"
    return rupiah(nilai)


def sematkan_properti(geojson: dict, lebar_tahun: pd.DataFrame, metrik: str) -> dict:
    """Menyalin GeoJSON dan menambahkan nilai terformat ke properti setiap provinsi."""
    g = copy.deepcopy(geojson)
    baris = lebar_tahun.set_index("kode_bps")
    m = METRIK[metrik]
    for f in g["features"]:
        kode = f["properties"]["kode_bps"]
        p = f["properties"]
        if kode in baris.index:
            r = baris.loc[kode]
            p["nilai"] = format_nilai(r[metrik], m.satuan)
            p["pendapatan"] = rupiah(r["pendapatan"])
            p["belanja"] = rupiah(r["belanja"])
            p["tkdd"] = rupiah(r["tkdd"])
            p["kemandirian"] = persen(r["kemandirian"])
            p["penduduk"] = orang(r["penduduk"])
        else:
            for k in ("nilai", "pendapatan", "belanja", "tkdd", "kemandirian", "penduduk"):
                p[k] = "tidak ada data"
    return g


def skala_legenda(satuan: str) -> tuple[float, str]:
    """Pembagi dan label satuan agar angka pada legenda tetap pendek."""
    if satuan == "persen":
        return 1.0, "%"
    if satuan == "rupiah_per_orang":
        return 1e6, "juta Rp per orang"
    return 1e12, "triliun Rp"


def buat_peta(geojson: dict, lebar_tahun: pd.DataFrame, metrik: str, tahun: int) -> folium.Map:
    """Membangun peta choropleth untuk satu metrik dan tahun."""
    m = METRIK[metrik]
    pembagi, satuan_legenda = skala_legenda(m.satuan)
    data = lebar_tahun[["kode_bps", metrik]].dropna().copy()
    data[metrik] = data[metrik] / pembagi
    peta = folium.Map(location=PUSAT_INDONESIA, zoom_start=4, tiles="OpenStreetMap", control_scale=True)
    peta.fit_bounds(BATAS_INDONESIA)

    folium.Choropleth(
        geo_data=geojson,
        data=data,
        columns=["kode_bps", metrik],
        key_on="feature.properties.kode_bps",
        fill_color=m.skema_warna,
        fill_opacity=0.8,
        line_opacity=0.4,
        nan_fill_color="#dddddd",
        legend_name=f"{m.nama}, {tahun} ({satuan_legenda})",
        bins=7,
        highlight=True,
    ).add_to(peta)

    g = sematkan_properti(geojson, lebar_tahun, metrik)
    folium.GeoJson(
        g,
        name="Keterangan",
        style_function=lambda _f: {"fillOpacity": 0, "color": "transparent", "weight": 0},
        highlight_function=lambda _f: {"weight": 2, "color": "#333333", "fillOpacity": 0.1},
        tooltip=folium.GeoJsonTooltip(
            fields=["provinsi", "nilai", "pendapatan", "belanja", "tkdd", "kemandirian", "penduduk"],
            aliases=[
                "Provinsi",
                m.nama,
                "Pendapatan",
                "Belanja",
                "Transfer pusat",
                "Kemandirian fiskal",
                "Penduduk",
            ],
            sticky=True,
            localize=False,
        ),
    ).add_to(peta)
    return peta
