"""Read back the plotted geometry of thesis Figures 9 and 11 from the DOCX vector shapes (read-only).

    python -I tools/figure_geometry.py
        -> outputs/figure11_curves.csv      cycle number and capacity retention per plotted curve
        -> outputs/figure9_points.csv       Pareto-front polyline vertices and highlighted markers
        -> outputs/figure_geometry_summary.json

What this is: a readout of the lines drawn in the figures, calibrated against the figures' own
grid lines and tick labels. What it is not: the data or code that produced the figures. A
plotted line shows what the author drew; it does not show how the numbers were obtained.

The DOCX was converted from a PDF by iLovePDF (docProps/custom.xml), so each figure exists as
a DrawingML group (used here) with a VML fallback. Coordinates are EMU; one EMU of the Figure 11
plot frame is 1.5e-5 percentage points of retention, far below any value read here.
"""

import hashlib
import json
import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[2]
DOCX = ROOT / "EURÉKA 2026 - KT.docx"
EXPECTED_SHA256 = "01363a069eeb005851f6d62ac4b9da9e3fd13a742bebbfdfc14c802f0eddff8c"
OUT = HERE / "outputs"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
}
W, A, WPS, WPG = ("{%s}" % NS[k] for k in ("w", "a", "wps", "wpg"))

FIG11_PARA = 3192   # paragraph holding the Figure 11 drawing (caption at 3211)
FIG9_PARA = 2032    # paragraph holding the Figure 9 drawing (caption at 2060)


def shapes(paragraph):
    """Return every sub-path of every wps:wsp in the paragraph as dict(off, ext, color, dash, pts).

    One wsp may hold several a:path elements (e.g. all tick marks of an axis); each becomes its
    own entry. Path coordinates are scaled to the shape extent when path w/h differ from it."""
    out = []
    for grp in paragraph.iter(WPG + "wgp"):
        x = grp.find(f"{WPG}grpSpPr/{A}xfrm")
        if x is not None:  # the converter writes identity group transforms; refuse anything else
            off, ext, choff, chext = (x.find(A + t) for t in ("off", "ext", "chOff", "chExt"))
            if choff is not None and (choff.attrib != {"x": off.get("x"), "y": off.get("y")}
                                      or chext.attrib != {"cx": ext.get("cx"), "cy": ext.get("cy")}):
                raise SystemExit("non-identity group transform; calibration below would be wrong")
    for sp in paragraph.iter(WPS + "wsp"):
        xfrm = sp.find(f"{WPS}spPr/{A}xfrm")
        if xfrm is None:
            continue
        off = (int(xfrm.find(A + "off").get("x")), int(xfrm.find(A + "off").get("y")))
        ext = (int(xfrm.find(A + "ext").get("cx")), int(xfrm.find(A + "ext").get("cy")))
        ln = sp.find(f"{WPS}spPr/{A}ln")
        clr = ln.find(f".//{A}srgbClr") if ln is not None else None
        dash = ln.find(f"{A}prstDash") if ln is not None else None
        for path in sp.iter(A + "path"):
            pw, ph = int(path.get("w", "0")), int(path.get("h", "0"))
            sx = ext[0] / pw if pw else 1.0
            sy = ext[1] / ph if ph else 1.0
            pts = [(int(p.get("x")) * sx, int(p.get("y")) * sy) for c in path for p in c.iter(A + "pt")]
            if pts:
                out.append({"off": off, "ext": ext,
                            "color": clr.get("val").upper() if clr is not None else None,
                            "dash": dash.get("val") if dash is not None else None, "pts": pts})
    return out


def figure11(par):
    sh = shapes(par)
    frame = next(s for s in sh if s["color"] == "000000" and len(s["pts"]) == 5 and s["ext"][1] > 2_000_000)
    fx, fy = frame["off"]
    width = max(p[0] for p in frame["pts"])
    height = max(p[1] for p in frame["pts"])
    # Calibration from the figure itself: x tick marks every 200 cycles (labels 0..1,400),
    # horizontal grid lines at 100/90/80/70 % retention from top to bottom.
    xticks = sorted({s["off"][0] - fx + s["pts"][0][0] for s in sh
                     if s["color"] == "7F7F7F" and len(s["pts"]) == 2 and s["pts"][0][0] == s["pts"][1][0]})
    ygrid = sorted({s["off"][1] - fy + s["pts"][0][1] for s in sh
                    if s["color"] == "BFBFBF" and len(s["pts"]) == 2 and s["pts"][0][1] == s["pts"][1][1]})
    emu_per_200cyc = np.diff(xticks).mean()
    emu_per_10pct = np.diff(ygrid).mean()
    legend = {("0000FF", "solid"): "Fixed Controller", ("FF0000", "dash"): "Adaptive LQR",
              ("009900", "dash"): "Pareto Optimal"}
    curves = {}
    for s in sh:
        if len(s["pts"]) < 20:
            continue
        name = legend[(s["color"], s["dash"])]
        x = np.array([s["off"][0] - fx + p[0] for p in s["pts"]], float)
        y = np.array([s["off"][1] - fy + p[1] for p in s["pts"]], float)
        curves[name] = (x / emu_per_200cyc * 200.0, 100.0 - y / emu_per_10pct * 10.0)
    # Legend order check: the three short legend samples are stacked top to bottom in this order.
    samples = sorted((s["off"][1], legend[(s["color"], s["dash"])]) for s in sh
                     if len(s["pts"]) == 3 and s["color"] in ("0000FF", "FF0000", "009900"))
    calib = {"frame_width_emu": width, "frame_height_emu": height,
             "x_tick_emu": xticks, "y_grid_emu": ygrid,
             "emu_per_200_cycles": emu_per_200cyc, "emu_per_10_pct": emu_per_10pct,
             "x_axis_end_cycles": width / emu_per_200cyc * 200.0,
             "legend_samples_top_to_bottom": [n for _, n in samples],
             "legend_text_in_docx": "Fixed Controller Adaptive LQR Pareto Optimal (para 3193)"}
    return curves, calib


def interp(xs, ys, x0):
    return float(np.interp(x0, xs, ys))


def fit_report(n, fade):
    """Least-squares fits of fade(N) through the origin; residuals in percentage points."""
    res = {}
    for label, cols in {"a*N": [n], "a*N + b*N^2": [n, n**2], "a*sqrt(N)": [np.sqrt(n)],
                        "a*sqrt(N) + b*N": [np.sqrt(n), n]}.items():
        X = np.column_stack(cols)
        coef, *_ = np.linalg.lstsq(X, fade, rcond=None)
        r = fade - X @ coef
        res[label] = {"coef": coef.tolist(), "max_abs_resid_pp": float(np.abs(r).max()),
                      "rms_resid_pp": float(np.sqrt((r**2).mean()))}
    return res


def figure9(par):
    sh = shapes(par)
    frame = next(s for s in sh if s["color"] == "000000" and len(s["pts"]) == 5)
    fx, fy = frame["off"]
    ygrid = sorted({s["off"][1] - fy + s["pts"][0][1] for s in sh
                    if s["color"] == "BFBFBF" and len(s["pts"]) == 2 and s["pts"][0][1] == s["pts"][1][1]})
    xgrid = sorted({s["off"][0] - fx + s["pts"][0][0] for s in sh
                    if s["color"] in ("BFBFBF", "000000") and len(s["pts"]) == 2
                    and s["pts"][0][0] == s["pts"][1][0] and abs(s["pts"][0][1] - s["pts"][1][1]) > 1_000_000})
    # Tick labels in the DOCX text: x 100 120 140 160 180 (Wh/km); y 5 4 3 2 1 top to bottom.
    ex = (max(xgrid) - min(xgrid)) / 80.0      # EMU per Wh/km
    ey = (max(ygrid) - min(ygrid)) / 4.0       # EMU per (%/1000 cycles)
    to_xy = lambda X, Y: (100.0 + (X - min(xgrid)) / ex, 5.0 - (Y - min(ygrid)) / ey)
    closed = lambda s: s["pts"][0] == s["pts"][-1]
    front = max((s for s in sh if s["color"] == "0000FF" and len(s["pts"]) >= 10 and not closed(s)),
                key=lambda s: len(s["pts"]))
    pts = [to_xy(front["off"][0] - fx + p[0], front["off"][1] - fy + p[1]) for p in front["pts"]]
    markers = []
    for s in sh:   # circular markers: closed 17-vertex outlines in a square box
        if len(s["pts"]) == 17 and closed(s) and s["ext"][0] == s["ext"][1]:
            cx = s["off"][0] - fx + s["ext"][0] / 2.0
            cy = s["off"][1] - fy + s["ext"][1] / 2.0
            markers.append((round(s["ext"][0]), *to_xy(cx, cy)))
    return pts, sorted(set((d, round(x, 3), round(y, 3)) for d, x, y in markers)), {"emu_per_Whkm": ex, "emu_per_unit_y": ey}


def main():
    digest = hashlib.sha256(DOCX.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"DOCX hash {digest} differs from the audited file")
    root = ET.fromstring(zipfile.ZipFile(DOCX, "r").read("word/document.xml"))
    paras = list(root.iter(W + "p"))
    OUT.mkdir(exist_ok=True)

    curves, calib = figure11(paras[FIG11_PARA])
    names = ["Fixed Controller", "Adaptive LQR", "Pareto Optimal"]
    n0 = curves[names[0]][0]
    for nm in names[1:]:
        if not np.allclose(curves[nm][0], n0, atol=1e-6):
            raise SystemExit("curves are sampled at different abscissae")
    with open(OUT / "figure11_curves.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["point", "cycle_number"] + [f"retention_pct_{n.replace(' ', '_')}" for n in names])
        for i, n in enumerate(n0):
            w.writerow([i, f"{n:.4f}"] + [f"{curves[nm][1][i]:.5f}" for nm in names])

    summary = {"source_sha256": digest, "figure11": {"calibration": calib, "points_per_curve": len(n0),
               "abscissa_spacing_cycles": sorted(set(np.round(np.diff(n0), 3).tolist())),
               "readout": {}, "fits": {}, "ratio_to_fixed": {}}}
    fade = {nm: 100.0 - curves[nm][1] for nm in names}
    for N in (500, 1000, 1500):
        row = {nm: interp(n0, fade[nm], N) for nm in names}
        row["relative_reduction_adaptive_vs_fixed_pct"] = 100 * (1 - row["Adaptive LQR"] / row["Fixed Controller"])
        row["relative_reduction_pareto_vs_fixed_pct"] = 100 * (1 - row["Pareto Optimal"] / row["Fixed Controller"])
        summary["figure11"]["readout"][f"fade_pp_at_{N}_cycles"] = row
    for nm in names:
        summary["figure11"]["fits"][nm] = fit_report(n0[1:], fade[nm][1:])
    for nm in names[1:]:
        r = fade[nm][5:] / fade["Fixed Controller"][5:]   # skip the first points where rounding dominates
        summary["figure11"]["ratio_to_fixed"][nm] = {"min": float(r.min()), "max": float(r.max())}
    # Where along the plotted horizon would the adaptive-vs-fixed reduction equal the abstract's 15.3 %?
    grid = np.linspace(1, 1500, 14991)
    red = 100 * (1 - np.interp(grid, n0, fade["Adaptive LQR"]) / np.interp(grid, n0, fade["Fixed Controller"]))
    hit = grid[np.argmin(np.abs(red - 15.3))]
    summary["figure11"]["cycles_where_reduction_equals_15.3pct"] = float(hit)
    summary["figure11"]["reduction_range_pct_over_10_to_1500_cycles"] = [float(red[grid >= 10].min()), float(red.max())]

    pts, markers, cal9 = figure9(paras[FIG9_PARA])
    with open(OUT / "figure9_points.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "marker_diameter_emu", "energy_Wh_per_km", "fade_pct_per_1000_cycles"])
        for x, y in pts:
            w.writerow(["front_vertex", "", f"{x:.4f}", f"{y:.4f}"])
        for d, x, y in markers:
            w.writerow(["marker", d, f"{x:.4f}", f"{y:.4f}"])
    summary["figure9"] = {"calibration": cal9, "front_vertices": [[round(x, 4), round(y, 4)] for x, y in pts],
                          "markers": markers}
    (OUT / "figure_geometry_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    f11 = summary["figure11"]
    print("Figure 11:", f11["points_per_curve"], "points/curve; x axis ends at",
          round(calib["x_axis_end_cycles"], 2), "cycles; legend", calib["legend_samples_top_to_bottom"])
    for k, v in f11["readout"].items():
        print(f"  {k}: " + ", ".join(f"{a}={b:.3f}" for a, b in v.items()))
    for nm, fits in f11["fits"].items():
        best = min(fits.items(), key=lambda kv: kv[1]["max_abs_resid_pp"])
        print(f"  best fit {nm}: {best[0]} coef={best[1]['coef']} max|resid|={best[1]['max_abs_resid_pp']:.2e} pp")
    print("  ratio to fixed:", f11["ratio_to_fixed"])
    print("Figure 9 front:", summary["figure9"]["front_vertices"])
    print("Figure 9 markers:", markers)


if __name__ == "__main__":
    main()
