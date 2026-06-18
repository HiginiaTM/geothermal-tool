from datetime import date


def fm(v):
    if v >= 1:    return f"${v:.1f}M"
    if v >= 0.1:  return f"${v*1000:.0f}k"
    return f"${v*1e6:.0f}"


def build_html_report(rp):
    p          = rp["p"]
    play       = rp["play"]
    proj       = rp["proj"]
    si         = rp["si"]
    lm         = rp["lm"]
    km2        = rp["km2"]
    area_val   = rp["area_val"]
    area_unit  = rp["area_unit"]
    depth_m    = rp["depth_m"]
    depth_str  = rp["depth_str"]
    dz         = rp["dz"]
    ph12lo     = rp["ph12lo"]
    ph12hi     = rp["ph12hi"]
    ph3lo      = rp["ph3lo"]
    ph3hi      = rp["ph3hi"]
    tlo        = rp["tlo"]
    thi        = rp["thi"]
    freq       = rp["include_freq"]
    by_phase   = rp["by_phase"]
    pub_items  = rp["pub_items"]
    con_items  = rp["con_items"]
    acq_items  = rp["acq_items"]
    have_items = rp["have_items"]
    seis2dlo   = rp["seis2dlo"]
    seis2dhi   = rp["seis2dhi"]
    seis3dlo   = rp["seis3dlo"]
    seis3dhi   = rp["seis3dhi"]
    a1_items   = rp["a1_items"]
    a2_items   = rp["a2_items"]

    today      = date.today().strftime("%B %d, %Y")
    title      = proj if proj else p["label"]
    area_str   = f"{area_val} {area_unit}" + (f" ({km2:.1f} km²)" if area_unit != "km²" else "")

    phase_labels = {
        "Ph.1": "Phase 1 — Preliminary Survey",
        "Ph.2": "Phase 2 — Surface Exploration",
        "Ph.3": "Phase 3 — Initial Subsurface Characterisation",
    }
    app_colors = {
        "Essential": {"bg": "#E1F5EE", "fg": "#0F6E56"},
        "Frequent":  {"bg": "#E6F1FB", "fg": "#185FA5"},
        "Optional":  {"bg": "#FAEEDA", "fg": "#854F0B"},
        "Rarely":    {"bg": "#FCEBEB", "fg": "#A32D2D"},
        "—":         {"bg": "#F1EFE8", "fg": "#5F5E5A"},
    }

    def tech_rows(ph):
        if ph not in by_phase:
            return ""
        rows = ""
        for t in by_phase[ph]:
            app = t[play]
            c   = app_colors.get(app, app_colors["—"])
            rows += f"""<tr>
              <td><span style="background:{c['bg']};color:{c['fg']};font-size:11px;font-weight:600;padding:2px 8px;border-radius:3px;display:inline-block">{app}</span></td>
              <td>{t['name']}</td>
              <td style="color:#666;font-size:12px">{t['cu']}</td>
            </tr>"""
        return rows

    def data_rows(items, bc):
        rows = ""
        for d in items:
            rows += f"""<tr>
              <td style="border-left:3px solid {bc};padding-left:10px;vertical-align:top">
                <strong>{d['name']}</strong><br>
                <span style="color:#888;font-size:11px">{d['rel']}</span>
              </td>
              <td style="color:#444;font-size:13px;vertical-align:top">{d['desc']}</td>
            </tr>"""
        return rows

    loc_note = ""
    if lm != 0:
        sign = "" if lm < 0 else "+"
        loc_note = f'<p style="font-size:12px;color:#888;margin-bottom:10px">{si["label"]}: {sign}{round(lm*100)}% — {si["reg"]}</p>'

    freq_card = ""
    if freq:
        freq_card = f'<div class="sc"><div class="l">Frequent uplift</div><div class="v">{fm(p["flo"]*(1+lm))} – {fm(p["fhi"]*(1+lm))}</div></div>'

    freq_note = ""
    if freq:
        freq_note = f'<p class="fn"><strong>Frequent uplift:</strong> {p["ft"]}</p>'

    have_section = ""
    if have_items:
        rows = "".join(f'<tr><td style="border-left:3px solid #9fc060;padding-left:10px;opacity:.75"><strong>{d["name"]}</strong><br><span style="font-size:11px;color:#888">{d["rel"]}</span></td><td style="font-size:12px;color:#999;font-style:italic">Confirmed available</td></tr>' for d in have_items)
        have_section = f'<tr class="dsr" style="border-left:3px solid #639922"><td colspan="2">Already have — {len(have_items)} dataset{"s" if len(have_items)>1 else ""} confirmed</td></tr>{rows}'

    a1_section = ""
    if a1_items:
        a1_section = f'<tr class="dsr" style="border-left:3px solid #1D9E75"><td colspan="2">A1 — Required &amp; in state databases (TX RRC, CA DOC, CO ECMC, UT DNR, WV DEP)</td></tr>{data_rows(a1_items,"#1D9E75")}'

    a2_section = ""
    if a2_items:
        a2_section = f'<tr class="dsr" style="border-left:3px solid #BA7517"><td colspan="2">A2 — Required but inconsistently digitized — may need manual retrieval</td></tr>{data_rows(a2_items,"#BA7517")}'

    con_section = ""
    if con_items:
        con_section = f'<tr class="dsr" style="border-left:3px solid #378ADD"><td colspan="2">B — O&amp;G consortium / data trade targets — operators would share anonymized</td></tr>{data_rows(con_items,"#378ADD")}'

    acq_section = ""
    if acq_items:
        acq_section = f'<tr class="dsr" style="border-left:3px solid #E24B4A"><td colspan="2">C — Must acquire independently — operators will NOT share</td></tr>{data_rows(acq_items,"#E24B4A")}'

    tech_section = ""
    for ph in ["Ph.1", "Ph.2", "Ph.3"]:
        if ph in by_phase:
            tech_section += f'<tr class="phr"><td colspan="3">{phase_labels[ph]}</td></tr>{tech_rows(ph)}'

    notes_html = "".join(f'<li style="padding:7px 0 7px 13px;border-left:3px solid {p["col"]};margin-bottom:5px;font-size:13px;color:#222">{n}</li>' for n in p["notes"])

    css = f"""*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#1a1a2e;background:#f2f4f8;font-size:14px;line-height:1.6}}
.page{{max-width:900px;margin:0 auto;padding:32px 20px 60px}}
.cover{{background:#1a1a2e;color:#fff;border-radius:12px;padding:40px 44px;margin-bottom:24px;position:relative;overflow:hidden}}
.bar{{position:absolute;left:0;top:0;bottom:0;width:5px;background:{p["col"]}}}
.tag{{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{p["col"]};margin-bottom:12px}}
.cover h1{{font-size:28px;font-weight:700;margin-bottom:6px}}
.sub{{font-size:14px;color:#7090b0;margin-bottom:24px}}
.mg{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.mi label{{display:block;font-size:10px;color:#607080;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px}}
.mi span{{font-size:13px;color:#b8d0e8}}
.cfoot{{margin-top:22px;font-size:11px;color:#405060;border-top:1px solid #2a3a4a;padding-top:10px}}
.card{{background:#fff;border-radius:10px;border:1px solid #e2e6ee;margin-bottom:20px;overflow:hidden}}
.ch{{padding:13px 20px;border-bottom:1px solid #eaecf0;display:flex;align-items:center;gap:10px;background:#fafbfc}}
.dot{{width:10px;height:10px;border-radius:50%}}
.ch h2{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#555}}
.cb{{padding:20px}}
.tot{{background:{p["coll"]};border:1px solid {p["col"]}50;border-radius:8px;padding:14px 18px;text-align:center;margin-bottom:14px}}
.tot .l{{font-size:12px;color:{p["col"]};font-weight:600;margin-bottom:3px}}
.tot .v{{font-size:26px;font-weight:700;color:#1a1a2e}}
.g3{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px}}
.g2{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:12px}}
.sc{{background:#f7f8fb;border:1px solid #e4e8f0;border-radius:8px;padding:11px 13px}}
.sc .l{{font-size:11px;color:#888;margin-bottom:3px}}
.sc .v{{font-size:15px;font-weight:600}}
.wl{{list-style:none}}
.wl li{{font-size:12px;color:#666;padding:3px 0 3px 10px;border-left:2px solid #dde;margin-bottom:2px}}
.crit{{background:#fffbee;border:1px solid #f0d888;border-radius:6px;padding:10px 13px;font-size:13px;color:#664400;margin-top:10px}}
.wb{{background:#eef6ff;border:1px solid #b8d4f0;border-radius:8px;padding:11px 15px;margin-bottom:12px;font-size:13px;color:#1a3a5c}}
.fn{{font-size:12px;color:#555;background:#f8f8f8;border:1px solid #eee;border-radius:6px;padding:8px 12px;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse}}
th{{text-align:left;font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #e8ecf0;padding:7px 8px}}
td{{padding:7px 8px;border-bottom:1px solid #f2f2f2;vertical-align:top}}
.tt tr:last-child td,.dt tr:last-child td{{border-bottom:none}}
.phr td{{background:#f5f7fa;font-size:11px;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.06em;padding:7px 8px;border-bottom:1px solid #e2e6ee}}
.dsr td{{background:#f5f7fa;font-size:11px;font-weight:700;color:#444;text-transform:uppercase;letter-spacing:.06em;padding:7px 8px;border-bottom:1px solid #e2e6ee}}
.nl{{list-style:none}}
.foot{{text-align:center;font-size:11px;color:#aaa;margin-top:28px;padding-top:16px;border-top:1px solid #e4e8ee;line-height:1.9}}
@media print{{body{{background:#fff}}.page{{padding:0}}.card{{break-inside:avoid}}}}"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Geothermal Report{" — " + proj if proj else ""}</title>
<style>{css}</style>
</head>
<body>
<div class="page">

<div class="cover">
  <div class="bar"></div>
  <div style="padding-left:14px">
    <div class="tag">Geothermal Exploration Decision Report</div>
    <h1>{title}</h1>
    <div class="sub">{p["label"]} &mdash; {p["sub"]} &mdash; {p["ex"]}</div>
    <div class="mg">
      <div class="mi"><label>State</label><span>{si["label"]}</span></div>
      <div class="mi"><label>Parcel area</label><span>{area_str}</span></div>
      <div class="mi"><label>Target depth</label><span>{depth_str} — {dz["label"]}</span></div>
      <div class="mi"><label>Programme scope</label><span>{"Essential + Frequent" if freq else "Essential only"}</span></div>
    </div>
    <div class="cfoot">Generated {today} &bull; All costs 2025–2026 USD &bull; Continental United States</div>
  </div>
</div>

<div class="card">
  <div class="ch"><div class="dot" style="background:#378ADD"></div><h2>Cost Estimate — 2025–2026 USD</h2></div>
  <div class="cb">
    {loc_note}
    <div class="tot"><div class="l">Total programme estimate</div><div class="v">{fm(tlo)} – {fm(thi)}</div></div>
    <div class="g3">
      <div class="sc"><div class="l">Ph.1+2 pre-drilling</div><div class="v">{fm(ph12lo)} – {fm(ph12hi)}</div></div>
      <div class="sc"><div class="l">Ph.3 pre full-size well</div><div class="v">{fm(ph3lo)} – {fm(ph3hi)}</div></div>
      {freq_card}
    </div>
    <p style="font-size:12px;color:#666;margin-bottom:8px">Seismic estimates for {km2:.1f} km² parcel:</p>
    <div class="g2">
      <div class="sc"><div class="l">2D seismic (parcel estimate)</div><div class="v">{fm(seis2dlo)} – {fm(seis2dhi)}</div></div>
      <div class="sc"><div class="l">3D seismic (if warranted)</div><div class="v">{fm(seis3dlo)} – {fm(seis3dhi)}</div></div>
    </div>
    <ul class="wl">
      <li>NEPA / permitting ($200k–$800k) included in Ph.1 totals</li>
      <li>Full-size exploration wells, DAS/DTS, stimulation and well testing NOT included</li>
      <li>Add ~15% for project management overhead</li>
      <li>Within-US variability ±20% around stated figures</li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="ch"><div class="dot" style="background:#E94560"></div><h2>Programme Timeline</h2></div>
  <div class="cb">
    <div class="g3">
      <div class="sc"><div class="l">Ph.1+2 field work</div><div class="v">{p["ph12d"]}</div></div>
      <div class="sc"><div class="l">Phase 3</div><div class="v">{p["ph3d"]}</div></div>
      <div class="sc"><div class="l">Total elapsed</div><div class="v">{p["totd"]}</div></div>
    </div>
    <div class="crit"><strong>Critical path:</strong> {p["crit"]}<br>
      <span style="font-size:12px">NEPA/permitting (12–36 months) typically runs in parallel — file permit applications at the same time as Phase 1 desk studies.</span>
    </div>
  </div>
</div>

<div class="card">
  <div class="ch"><div class="dot" style="background:#1D9E75"></div><h2>Acquisition Campaign</h2></div>
  <div class="cb">
    <div class="wb"><strong>Phase 3 well programme:</strong> {p["hfw"]} heat flow / TG wells (&lt;500 m) at 15–20 km spacing &nbsp;+&nbsp; {p["shw"]} slim-hole diamond core wells (up to {depth_str})</div>
    <p style="font-size:13px;color:#333;margin-bottom:10px"><strong>Key cost drivers:</strong> {p["drv"]}</p>
    {freq_note}
    <table class="tt">
      <thead><tr><th style="width:110px">Priority</th><th>Technique</th><th style="width:160px">Unit cost</th></tr></thead>
      <tbody>{tech_section}</tbody>
    </table>
  </div>
</div>

<div class="card">
  <div class="ch"><div class="dot" style="background:#BA7517"></div><h2>Data Acquisition Strategy</h2></div>
  <div class="cb">
    <table class="dt">
      <thead><tr><th style="width:220px">Dataset</th><th>Notes &amp; sources</th></tr></thead>
      <tbody>{have_section}{a1_section}{a2_section}{con_section}{acq_section}</tbody>
    </table>
  </div>
</div>

<div class="card">
  <div class="ch"><div class="dot" style="background:{p["col"]}"></div><h2>Play-Specific Notes &amp; Recommendations</h2></div>
  <div class="cb">
    <ul class="nl">{notes_html}</ul>
  </div>
</div>

<div class="foot">
  All costs in 2025–2026 USD &bull; Continental United States &bull; Order-of-magnitude guidance &bull; ±20% within-US variability<br>
  Sources: IGA Best Practices Guide (2nd ed.) &bull; Fervo Energy S-1 IPO filing (April 2026) &bull; DOE GeoVision Study (2019) &bull; DOE EGS Shot Analysis (2023) &bull; SLB drilling cost data
</div>

</div>
</body>
</html>"""
