import streamlit as st
from datetime import date
from data import PLAYS, TECHNIQUES, DATA_ITEMS, STATE_DATA, DEPTH_ZONES
from report import build_html_report

st.set_page_config(
    page_title="Geothermal Exploration Decision Tool",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .stSelectbox label, .stNumberInput label, .stSlider label, .stTextInput label { font-size: 13px; }
    div[data-testid="stSidebarContent"] { padding-top: 1rem; }
    .report-header { background: #1a1a2e; color: white; padding: 1.5rem 2rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 5px solid #1D9E75; }
    .metric-card { background: #f8f9fb; border: 1px solid #e4e8f0; border-radius: 8px; padding: 12px 16px; text-align: center; }
    .metric-label { font-size: 11px; color: #888; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 20px; font-weight: 600; color: #1a1a2e; }
    .total-box { background: #E6F1FB; border: 1px solid #378ADD; border-radius: 8px; padding: 16px; text-align: center; margin-bottom: 1rem; }
    .total-label { font-size: 12px; color: #185FA5; font-weight: 600; }
    .total-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
    .warn-item { font-size: 12px; color: #666; padding: 3px 0 3px 10px; border-left: 2px solid #dde; margin-bottom: 3px; }
    .section-title { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #555; border-bottom: 1px solid #e8ecf0; padding-bottom: 6px; margin-bottom: 12px; margin-top: 20px; }
    .tech-row { display: flex; align-items: flex-start; gap: 8px; padding: 6px 10px; background: white; border: 1px solid #e8ecf0; border-radius: 6px; margin-bottom: 4px; }
    .badge-essential { background: #E1F5EE; color: #0F6E56; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 3px; }
    .badge-frequent  { background: #E6F1FB; color: #185FA5; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 3px; }
    .badge-optional  { background: #FAEEDA; color: #854F0B; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 3px; }
    .badge-rarely    { background: #FCEBEB; color: #A32D2D; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 3px; }
    .data-pub  { border-left: 3px solid #1D9E75; padding-left: 10px; margin-bottom: 6px; }
    .data-con  { border-left: 3px solid #378ADD; padding-left: 10px; margin-bottom: 6px; }
    .data-acq  { border-left: 3px solid #E24B4A; padding-left: 10px; margin-bottom: 6px; }
    .data-have { border-left: 3px solid #639922; padding-left: 10px; margin-bottom: 6px; opacity: 0.7; }
    .note-item { padding: 7px 0 7px 13px; border-left: 3px solid #1D9E75; margin-bottom: 6px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar inputs ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌋 Geothermal Decision Tool")
    st.markdown("---")

    st.markdown("### Project")
    project_name = st.text_input("Project name (optional)", placeholder="e.g. Project Vulcan")

    play_options = list(PLAYS.keys())
    play_labels  = [PLAYS[k]["label"] for k in play_options]
    play_idx = st.selectbox("Play type", range(len(play_options)),
                            format_func=lambda i: play_labels[i])
    play_key = play_options[play_idx]
    p = PLAYS[play_key]

    st.markdown("### Location")
    state_options = list(STATE_DATA.keys())
    state_labels  = [STATE_DATA[k]["label"] for k in state_options]
    state_idx = st.selectbox("State", range(len(state_options)),
                              format_func=lambda i: state_labels[i],
                              index=state_options.index("OTHER"))
    state_code = state_options[state_idx]
    si = STATE_DATA[state_code]
    lm = si["mod"]
    if lm != 0:
        col = "green" if lm < 0 else "red"
        sign = "" if lm < 0 else "+"
        st.markdown(f"<span style='color:{'#1D9E75' if lm<0 else '#E24B4A'};font-size:12px;font-weight:600'>{sign}{round(lm*100)}% cost {'reduction' if lm<0 else 'uplift'}</span> — {si['reg']}", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:#888;font-size:12px'>Baseline costs — {si['reg']}</span>", unsafe_allow_html=True)

    st.markdown("### Parcel")
    col1, col2 = st.columns([2, 1])
    with col1:
        area_val = st.number_input("Area", min_value=0.1, value=50.0, step=1.0)
    with col2:
        area_unit = st.selectbox("Unit", ["km²", "acres", "mi²"])

    def to_km2(v, u):
        if u == "acres":  return v * 0.00404686
        if u == "mi²":   return v * 2.58999
        return v

    km2 = to_km2(area_val, area_unit)
    if area_unit != "km²":
        st.markdown(f"<span style='font-size:11px;color:#888'>= {km2:.1f} km²</span>", unsafe_allow_html=True)

    st.markdown("### Target Depth")
    depth_m = st.slider("Depth (metres)", min_value=100, max_value=5000, value=2500, step=100)
    dz = next((z for z in DEPTH_ZONES if depth_m <= z["max"]), DEPTH_ZONES[-1])
    depth_str = f"{depth_m/1000:.2g} km" if depth_m >= 1000 else f"{depth_m} m"
    st.markdown(f"<span style='font-size:11px;color:#888'>{dz['label']}</span>", unsafe_allow_html=True)

    st.markdown("### Programme Scope")
    scope = st.radio("Include techniques rated:", ["Essential only (minimum)", "Essential + Frequent (recommended)"], index=1)
    include_freq = "Frequent" in scope

    st.markdown("---")
    generate = st.button("🔍 Generate Report", type="primary", use_container_width=True)

    st.markdown("### Data You Already Have")
    st.markdown("<span style='font-size:11px;color:#888'>Check all that apply</span>", unsafe_allow_html=True)

    have_data = []
    cat_labels = {
        "A1": ("🟢 A1 — Required & in state DBs", "#0F6E56"),
        "A2": ("🟡 A2 — Required but inconsistent", "#854F0B"),
        "B":  ("🔵 B — Consortium / share", "#185FA5"),
        "C":  ("🔴 C — Competitive, won't share", "#A32D2D"),
    }
    for cat, (cat_label, cat_color) in cat_labels.items():
        st.markdown(f"<span style='font-size:11px;font-weight:600;color:{cat_color}'>{cat_label}</span>", unsafe_allow_html=True)
        for item in [d for d in DATA_ITEMS if d["cat"] == cat]:
            if st.checkbox(item["name"], key=f"cb_{item['name']}", label_visibility="visible"):
                have_data.append(item["name"])


# ── Main panel ──────────────────────────────────────────────────
if not generate:
    st.markdown("""
    <div style='text-align:center;padding:80px 20px;color:#888'>
        <div style='font-size:48px;margin-bottom:16px'>🌋</div>
        <div style='font-size:20px;font-weight:500;color:#444;margin-bottom:8px'>Geothermal Exploration Decision Tool</div>
        <div style='font-size:14px'>Fill in the inputs on the left and click <strong>Generate Report</strong></div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Calculations ────────────────────────────────────────────────
ph12lo = p["ph12lo"] * (1 + lm)
ph12hi = p["ph12hi"] * (1 + lm)
ph3lo  = p["ph3lo"]  * (1 + lm) * dz["dm"]
ph3hi  = p["ph3hi"]  * (1 + lm) * dz["dm"]
tlo = ph12lo + ph3lo
thi = ph12hi + ph3hi
if include_freq:
    tlo += p["flo"] * (1 + lm)
    thi += p["fhi"] * (1 + lm)

seis2dlo = km2 * 0.5 * 15000  / 1e6
seis2dhi = km2 * 0.5 * 50000  / 1e6
seis3dlo = km2 * 0.3 * 50000  / 1e6
seis3dhi = km2 * 0.3 * 180000 / 1e6

AR = {"Essential": 1, "Frequent": 2, "Optional": 3, "Rarely": 4, "—": 5}
max_rank = 2 if include_freq else 1
techs = [t for t in TECHNIQUES if AR.get(t[play_key], 5) <= max_rank]
by_phase = {}
for t in techs:
    by_phase.setdefault(t["ph"], []).append(t)

have_set   = set(have_data)
pub_items  = [d for d in DATA_ITEMS if d["name"] not in have_set and d["cat"] in ("A1","A2")]
con_items  = [d for d in DATA_ITEMS if d["name"] not in have_set and d["cat"] == "B"]
acq_items  = [d for d in DATA_ITEMS if d["name"] not in have_set and d["cat"] == "C"]
have_items = [d for d in DATA_ITEMS if d["name"] in have_set]

def fm(v):
    if v >= 1:   return f"${v:.1f}M"
    if v >= 0.1: return f"${v*1000:.0f}k"
    return f"${v*1e6:.0f}"


# ── Report header ────────────────────────────────────────────────
area_str = f"{area_val} {area_unit}" + (f" ({km2:.1f} km²)" if area_unit != "km²" else "")
title = project_name if project_name else p["label"]

st.markdown(f"""
<div class="report-header" style="border-left-color:{p['col']}">
  <div style='font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{p['col']};margin-bottom:8px'>Geothermal Exploration Decision Report</div>
  <div style='font-size:26px;font-weight:700;margin-bottom:4px'>{title}</div>
  <div style='font-size:14px;color:#7090b0;margin-bottom:16px'>{p['label']} — {p['sub']}</div>
  <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px'>
    <div><div style='font-size:10px;color:#607080;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px'>State</div><div style='font-size:13px;color:#b8d0e8'>{si['label']}</div></div>
    <div><div style='font-size:10px;color:#607080;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px'>Parcel area</div><div style='font-size:13px;color:#b8d0e8'>{area_str}</div></div>
    <div><div style='font-size:10px;color:#607080;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px'>Target depth</div><div style='font-size:13px;color:#b8d0e8'>{depth_str}</div></div>
    <div><div style='font-size:10px;color:#607080;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px'>Scope</div><div style='font-size:13px;color:#b8d0e8'>{'Essential + Frequent' if include_freq else 'Essential only'}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Costs", "⏱ Timeline & Campaign", "📂 Data Strategy", "📋 Notes", "⬇️ Export"])

with tab1:
    if lm != 0:
        sign = "" if lm < 0 else "+"
        st.markdown(f"<span style='font-size:12px;color:#888'>{si['label']} location adjustment: {sign}{round(lm*100)}% — {si['reg']}</span>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="total-box" style="background:{p['coll']};border-color:{p['col']}">
      <div class="total-label" style="color:{p['col']}">Total programme estimate</div>
      <div class="total-value">{fm(tlo)} – {fm(thi)}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Ph.1+2 pre-drilling</div><div class="metric-value">{fm(ph12lo)} – {fm(ph12hi)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Ph.3 pre full-size well</div><div class="metric-value">{fm(ph3lo)} – {fm(ph3hi)}</div></div>', unsafe_allow_html=True)
    with c3:
        if include_freq:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Frequent uplift</div><div class="metric-value">{fm(p["flo"]*(1+lm))} – {fm(p["fhi"]*(1+lm))}</div></div>', unsafe_allow_html=True)

    st.markdown(f"<div class='section-title' style='margin-top:16px'>Seismic estimates for {km2:.1f} km² parcel</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">2D seismic (parcel estimate)</div><div class="metric-value">{fm(seis2dlo)} – {fm(seis2dhi)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">3D seismic (if warranted)</div><div class="metric-value">{fm(seis3dlo)} – {fm(seis3dhi)}</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
    for w in ["NEPA / permitting ($200k–$800k) included in Ph.1 totals",
              "Full-size exploration wells, DAS/DTS, stimulation and well testing NOT included",
              "Add ~15% for project management overhead",
              "Within-US variability ±20% around stated figures"]:
        st.markdown(f'<div class="warn-item">⚠ {w}</div>', unsafe_allow_html=True)


with tab2:
    st.markdown("<div class='section-title'>Programme timeline</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Ph.1+2 field work</div><div class="metric-value" style="font-size:16px">{p["ph12d"]}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Phase 3</div><div class="metric-value" style="font-size:16px">{p["ph3d"]}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total elapsed</div><div class="metric-value" style="font-size:16px">{p["totd"]}</div></div>', unsafe_allow_html=True)
    st.info(f"**Critical path:** {p['crit']}  \nNEPA/permitting (12–36 months) typically runs in parallel — file permit applications at the same time as Phase 1 desk studies.")

    st.markdown("<div class='section-title'>Acquisition campaign</div>", unsafe_allow_html=True)
    st.info(f"**Phase 3 well programme:** {p['hfw']} heat flow / TG wells (<500 m) at 15–20 km spacing  +  {p['shw']} slim-hole diamond core wells (up to {depth_str})")
    st.markdown(f"**Key cost drivers:** {p['drv']}")
    if include_freq:
        st.markdown(f"**Frequent uplift techniques:** {p['ft']}")

    phase_labels = {"Ph.1": "Phase 1 — Preliminary Survey", "Ph.2": "Phase 2 — Surface Exploration", "Ph.3": "Phase 3 — Subsurface Characterisation"}
    badge_class  = {"Essential": "badge-essential", "Frequent": "badge-frequent", "Optional": "badge-optional", "Rarely": "badge-rarely", "—": "badge-rarely"}

    for ph in ["Ph.1", "Ph.2", "Ph.3"]:
        if ph not in by_phase:
            continue
        st.markdown(f"<div class='section-title'>{phase_labels[ph]}</div>", unsafe_allow_html=True)
        for t in by_phase[ph]:
            app = t[play_key]
            bc  = badge_class.get(app, "badge-rarely")
            st.markdown(f"""
            <div class="tech-row">
              <span class="{bc}">{app}</span>
              <div>
                <div style='font-size:13px'>{t['name']}</div>
                <div style='font-size:11px;color:#888'>{t['cu']}</div>
              </div>
            </div>""", unsafe_allow_html=True)


with tab3:
    if have_items:
        st.markdown("<div class='section-title' style='color:#639922'>✓ Already have</div>", unsafe_allow_html=True)
        for d in have_items:
            st.markdown(f'<div class="data-have"><strong>{d["name"]}</strong> <span style="font-size:11px;color:#888">[{d["rel"]}]</span></div>', unsafe_allow_html=True)

    a1 = [d for d in pub_items if d["cat"]=="A1"]
    a2 = [d for d in pub_items if d["cat"]=="A2"]

    if a1:
        st.markdown("<div class='section-title' style='color:#0F6E56'>🟢 A1 — Required & in state databases</div>", unsafe_allow_html=True)
        st.caption("TX RRC, CA DOC, CO ECMC, UT DNR, WV DEP")
        for d in a1:
            st.markdown(f'<div class="data-pub"><strong>{d["name"]}</strong> <span style="font-size:11px;color:#888">[{d["rel"]}]</span><br><span style="font-size:12px;color:#555">{d["desc"]}</span></div>', unsafe_allow_html=True)

    if a2:
        st.markdown("<div class='section-title' style='color:#854F0B'>🟡 A2 — Required but inconsistently digitized</div>", unsafe_allow_html=True)
        st.caption("May need manual retrieval or records request")
        for d in a2:
            st.markdown(f'<div class="data-pub" style="border-color:#BA7517"><strong>{d["name"]}</strong> <span style="font-size:11px;color:#888">[{d["rel"]}]</span><br><span style="font-size:12px;color:#555">{d["desc"]}</span></div>', unsafe_allow_html=True)

    if con_items:
        st.markdown("<div class='section-title' style='color:#185FA5'>🔵 B — O&G consortium / data trade targets</div>", unsafe_allow_html=True)
        st.caption("Operators would share anonymized — de-risking incentive")
        for d in con_items:
            st.markdown(f'<div class="data-con"><strong>{d["name"]}</strong> <span style="font-size:11px;color:#888">[{d["rel"]}]</span><br><span style="font-size:12px;color:#555">{d["desc"]}</span></div>', unsafe_allow_html=True)

    if acq_items:
        st.markdown("<div class='section-title' style='color:#A32D2D'>🔴 C — Must acquire independently</div>", unsafe_allow_html=True)
        st.caption("Operators will NOT share — collect through new surveys or academic sources")
        for d in acq_items:
            st.markdown(f'<div class="data-acq"><strong>{d["name"]}</strong> <span style="font-size:11px;color:#888">[{d["rel"]}]</span><br><span style="font-size:12px;color:#555">{d["desc"]}</span></div>', unsafe_allow_html=True)


with tab4:
    st.markdown("<div class='section-title'>Play-specific notes & recommendations</div>", unsafe_allow_html=True)
    for note in p["notes"]:
        st.markdown(f'<div class="note-item" style="border-color:{p["col"]}">{note}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("All costs in 2025–2026 USD · Continental United States · Order-of-magnitude guidance · ±20% within-US variability  \nSources: IGA Best Practices Guide (2nd ed.) · Fervo Energy S-1 IPO filing (April 2026) · DOE GeoVision Study (2019) · DOE EGS Shot Analysis (2023) · SLB drilling cost data")


with tab5:
    st.markdown("### Download formatted HTML report")
    st.markdown("Click the button below to download a fully styled HTML report you can open in any browser, print, or share.")

    report_params = dict(
        play=play_key, p=p, proj=project_name, si=si, lm=lm,
        km2=km2, area_val=area_val, area_unit=area_unit,
        depth_m=depth_m, depth_str=depth_str, dz=dz,
        ph12lo=ph12lo, ph12hi=ph12hi, ph3lo=ph3lo, ph3hi=ph3hi,
        tlo=tlo, thi=thi, include_freq=include_freq,
        by_phase=by_phase, pub_items=pub_items, con_items=con_items,
        acq_items=acq_items, have_items=have_items,
        seis2dlo=seis2dlo, seis2dhi=seis2dhi,
        seis3dlo=seis3dlo, seis3dhi=seis3dhi,
        a1_items=a1, a2_items=a2,
    )
    html_report = build_html_report(report_params)

    filename = f"geothermal_report{'_'+project_name.replace(' ','_') if project_name else ''}.html"
    st.download_button(
        label="⬇️  Download HTML Report",
        data=html_report,
        file_name=filename,
        mime="text/html",
        type="primary",
        use_container_width=True,
    )
    st.caption("Save the file, then open it in Chrome, Safari, or Firefox. Use File → Print to save as PDF.")
