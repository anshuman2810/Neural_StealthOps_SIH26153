import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets the background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    """Sets inner margins/padding of a table cell in dxa (1/20 pt)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)

def set_table_borders(table, color="D1D5DB", sz="4", val="single"):
    """Applies clean subtle borders to the table."""
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)

def build_2col_table(doc, headers, data, col_widths=(Inches(2.6), Inches(4.2))):
    """Creates a beautifully styled 2-column Word table."""
    table = doc.add_table(rows=len(data) + 1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)

    # Style Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "1E293B")  # Dark slate
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=180, right=180)
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.bold = True
            run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.name = "Arial"

    # Style Data Rows
    for row_idx, (col1_text, col2_text) in enumerate(data, start=1):
        row_cells = table.rows[row_idx].cells
        row_cells[0].width = col_widths[0]
        row_cells[1].width = col_widths[1]

        row_cells[0].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        row_cells[1].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(row_cells[0], bg_color)
        set_cell_background(row_cells[1], bg_color)

        set_cell_margins(row_cells[0], top=120, bottom=120, left=180, right=180)
        set_cell_margins(row_cells[1], top=120, bottom=120, left=180, right=180)

        # Populate cell 0
        p0 = row_cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p0.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(col1_text)
        r0.font.size = Pt(9.5)
        r0.font.name = "Arial"
        r0.font.color.rgb = RGBColor(15, 23, 42)
        if ":" in col1_text:
            parts = col1_text.split(":", 1)
            p0.text = ""
            run_b = p0.add_run(parts[0] + ":")
            run_b.font.bold = True
            run_b.font.size = Pt(9.5)
            run_b.font.name = "Arial"
            run_b.font.color.rgb = RGBColor(15, 23, 42)
            run_r = p0.add_run(parts[1])
            run_r.font.size = Pt(9.5)
            run_r.font.name = "Arial"
            run_r.font.color.rgb = RGBColor(71, 85, 105)

        # Populate cell 1
        p1 = row_cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(2)
        if ":" in col2_text:
            parts = col2_text.split(":", 1)
            run_b = p1.add_run(parts[0] + ":")
            run_b.font.bold = True
            run_b.font.size = Pt(9.5)
            run_b.font.name = "Arial"
            run_b.font.color.rgb = RGBColor(15, 23, 42)
            run_r = p1.add_run(parts[1])
            run_r.font.size = Pt(9.5)
            run_r.font.name = "Arial"
            run_r.font.color.rgb = RGBColor(51, 65, 85)
        else:
            r1 = p1.add_run(col2_text)
            r1.font.size = Pt(9.5)
            r1.font.name = "Arial"
            r1.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

def main():
    out_path = Path("d:/Cybersec/SIH/predictive_world_model_tables.docx")
    doc = docx.Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Document Header
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("Predictive Network World Model — Evaluation & Defense Tables")
    r_title.font.bold = True
    r_title.font.size = Pt(18)
    r_title.font.name = "Arial"
    r_title.font.color.rgb = RGBColor(15, 23, 42)
    p_title.paragraph_format.space_after = Pt(2)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Smart India Hackathon (SIH) — AI Based Network Attack Forecasting")
    r_sub.font.italic = True
    r_sub.font.size = Pt(11)
    r_sub.font.name = "Arial"
    r_sub.font.color.rgb = RGBColor(100, 116, 139)
    p_sub.paragraph_format.space_after = Pt(14)

    # Context Note Box
    p_note = doc.add_paragraph()
    p_note.paragraph_format.left_indent = Inches(0.2)
    p_note.paragraph_format.right_indent = Inches(0.2)
    p_note.paragraph_format.space_after = Pt(16)
    r_note = p_note.add_run(
        "Project Scope: Implemented end-to-end flow-level telemetry analysis and forecasting. Evaluated on CSE-CIC-IDS2018 "
        "(10 capture files, 16.2M flows, 6.88 GB). Multi-Task Attention-LSTM World Model with +10s/+30s/+60s direct prediction "
        "heads, 60s autoregressive rollout, and dual XAI diagnostics."
    )
    r_note.font.size = Pt(9.5)
    r_note.font.italic = True
    r_note.font.name = "Arial"
    r_note.font.color.rgb = RGBColor(71, 85, 105)

    # 1. Uniqueness Table
    h1 = doc.add_heading(level=2)
    r_h1 = h1.add_run("1. Uniqueness (What Makes It Different)")
    r_h1.font.bold = True
    r_h1.font.size = Pt(13)
    r_h1.font.name = "Arial"
    r_h1.font.color.rgb = RGBColor(30, 41, 59)
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(6)

    uniqueness_data = [
        ("Reactive Detection: Alerts after the attack has already succeeded.",
         "Predictive Forecasting: Gives 30 to 60 seconds advance warning before damage occurs."),
        ("Single-Flow View: Looks at isolated packets with no past context.",
         "Full History View: Learns network patterns over a 2-minute sliding window."),
        ("No Simulation: Cannot predict what happens next.",
         "Future Rollout: Simulates the next 60 seconds of traffic trajectory."),
        ("Generic Alerts: Shows basic binary tags ('Malicious' or 'Anomaly').",
         "MITRE ATT&CK Stages: Pinpoints exact stage (Initial Access, Lateral Movement, Impact)."),
        ("Black-Box AI: Analysts cannot see why an alert was triggered.",
         "Explainable AI: Shows exact time window and network signals causing the alert."),
        ("Slow Manual Triage: Analysts waste hours investigating false alarms.",
         "Automated Playbooks: Suggests instant firewall blocks and host quarantine before breach.")
    ]
    build_2col_table(doc, ["Traditional Security Tools", "Our Predictive World Model"], uniqueness_data)

    # 2. Feasibility Table
    h2 = doc.add_heading(level=2)
    r_h2 = h2.add_run("2. Feasibility (Why It Can Actually Be Deployed)")
    r_h2.font.bold = True
    r_h2.font.size = Pt(13)
    r_h2.font.name = "Arial"
    r_h2.font.color.rgb = RGBColor(30, 41, 59)
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(6)

    feasibility_data = [
        ("Real-Time Speed",
         "Runs in ~4.2 milliseconds per 10-second window (uses <0.2% of compute time)."),
        ("Low Hardware Cost",
         "Runs on standard laptops or basic servers; model size is only 263 KB."),
        ("Low Memory Usage",
         "Uses <1.5 GB RAM even while handling millions of network flow records."),
        ("Air-Gapped & Offline",
         "Works 100% locally with zero cloud dependencies or outside API calls."),
        ("Standard Compatibility",
         "Ingests standard NetFlow/IPFIX logs; connects directly to existing SIEM tools."),
        ("Easy Operations",
         "Includes a simple browser-based dashboard with play/pause controls and threat gauges.")
    ]
    build_2col_table(doc, ["Practical Requirement", "How Our Solution Delivers"], feasibility_data)

    # 3. Challenges & Solutions Table
    h3 = doc.add_heading(level=2)
    r_h3 = h3.add_run("3. Challenges & Solutions (Problems Faced & Solved)")
    r_h3.font.bold = True
    r_h3.font.size = Pt(13)
    r_h3.font.name = "Arial"
    r_h3.font.color.rgb = RGBColor(30, 41, 59)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(6)

    challenges_data = [
        ("Too Much Normal Traffic: >90% of traffic is benign, so AI tends to ignore attacks.",
         "Class-Weighted Training: Penalizes missed attacks to achieve 100% attack recall."),
        ("Massive Data Size: Millions of flows cause computer memory to crash.",
         "Chunked Processing: Ingests data in small batches of 100k rows without high RAM usage."),
        ("Prediction Drift: Re-feeding predictions forward causes errors to multiply.",
         "Direct Forecast Heads: Dedicated predictors for +10s, +30s, and +60s in parallel."),
        ("Detecting Port Scans: Hard to distinguish wide port scans from targeted service floods.",
         "Port Entropy Math: Uses Shannon port diversity to separate scans from heavy floods."),
        ("Dirty / Corrupted Data: Raw dataset contains shifted columns and broken timestamps.",
         "Automated Cleaner: Filters out corrupted rows and invalid timestamps automatically."),
        ("Analyst Distrust of AI: Security teams reject AI they cannot understand.",
         "Built-in Explainability: Shows top network drivers (e.g., RST Flag +34%, Port Entropy Drop +22%).")
    ]
    build_2col_table(doc, ["Real-World Challenge", "Our Simple Solution"], challenges_data)

    # 4. Impact & Benefits Table
    h4 = doc.add_heading(level=2)
    r_h4 = h4.add_run("4. Impact & Benefits (Value Delivered)")
    r_h4.font.bold = True
    r_h4.font.size = Pt(13)
    r_h4.font.name = "Arial"
    r_h4.font.color.rgb = RGBColor(30, 41, 59)
    h4.paragraph_format.space_before = Pt(8)
    h4.paragraph_format.space_after = Pt(6)

    impact_data = [
        ("SOC Analysts (Tier-1/2)",
         "Slashes alert fatigue by >80% by replacing millions of raw alerts with clean 10s state timelines and clear MITRE stages."),
        ("Incident Response Teams",
         "Grants 30 to 60 seconds advance warning to isolate compromised hosts and deploy firewall filters before damage occurs."),
        ("Critical Infrastructure (CII)",
         "Delivers 100% recall on tested attack transitions, preventing stealthy lateral movement in defense, banking, and energy grids."),
        ("Financial & Cost Savings",
         "Avoids costly breach downtime and ransomware impacts (averaging $4.45M per breach) with zero expensive cloud API fees."),
        ("Automated Defense (SOAR)",
         "Triggers instant, pre-approved mitigation playbooks (firewall rules, host quarantine) without waiting for manual human triage."),
        ("Low Compute & Energy",
         "Ultra-lightweight 263 KB model consumes minimal CPU/GPU power compared to massive 100B+ parameter generative LLMs.")
    ]
    build_2col_table(doc, ["Target Stakeholder / Operational Area", "Impact & Practical Benefit Delivered"], impact_data)

    # 5. Practical Research & References Table
    h5 = doc.add_heading(level=2)
    r_h5 = h5.add_run("5. Research Sources & Practical References")
    r_h5.font.bold = True
    r_h5.font.size = Pt(13)
    r_h5.font.name = "Arial"
    r_h5.font.color.rgb = RGBColor(30, 41, 59)
    h5.paragraph_format.space_before = Pt(8)
    h5.paragraph_format.space_after = Pt(6)

    references_data = [
        ("CSE-CIC-IDS2018 Dataset Paper: Sharafaldin et al. (ICISSP 2018)",
         "Source of the 10 capture files (16.2M flows, 6.88 GB) used for data cleaning, state building, and multi-attack evaluation."),
        ("Port Scan Entropy Detection: Lakhina et al. (ACM SIGCOMM)",
         "Provided the Shannon entropy formula (-sum p log2 p) used in our 10s state builder to detect port scans vs DDoS floods."),
        ("Recurrent Temporal Modeling: Hochreiter & Schmidhuber (1997)",
         "Foundation for our 2-layer LSTM backbone that processes 12-window history (2 minutes) to learn state transition dynamics."),
        ("Self-Attention Pooling: Vaswani et al. (NeurIPS 2017)",
         "Architecture for our attention scoring layer (Linear -> Tanh -> Linear -> Softmax) showing which past window triggered the alarm."),
        ("Gradient x Input Feature Attribution: Shrikumar et al. (ICML 2017)",
         "Used in our XAI module (|grad * input|) to rank top physical telemetry drivers (e.g., RST flag surge, flow packet drop)."),
        ("MITRE ATT&CK Enterprise Matrix: MITRE Corporation (v14)",
         "Standard framework used to map raw dataset labels (Ares Bot, Slowloris, SSH-Bruteforce) into 7 tactical attack stages."),
        ("IETF IPFIX / NetFlow Standard: RFC 7011 / RFC 5101",
         "Defines the flow metadata schema (packet counts, byte volumes, TCP flag masks, duration, IAT) ingested by our pipeline.")
    ]
    build_2col_table(doc, ["Reference / Standard / Research Paper", "Direct Practical Use in Our Project"], references_data)

    try:
        doc.save(out_path)
        print(f"Successfully updated: {out_path.resolve()}")
    except PermissionError:
        alt_path = Path("d:/Cybersec/SIH/predictive_world_model_all_tables.docx")
        doc.save(alt_path)
        print(f"[!] Original file is open in Word. Saved updated document with all 5 tables to: {alt_path.resolve()}")

if __name__ == "__main__":
    main()
