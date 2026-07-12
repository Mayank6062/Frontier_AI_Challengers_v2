"""
html_styles_enterprise.py — Microsoft Architecture Center Quality CSS
=======================================================================
 
Professional enterprise styling matching gold standard architecture documentation.
"""
 
 
def get_enterprise_css() -> str:
    """Return complete CSS for enterprise HTML documentation."""
    return """/* ═══════════════════════════════════════════════════════════════════
   ENTERPRISE ARCHITECTURE DOCUMENTATION STYLES
   Microsoft Architecture Center Quality Standards
   ═══════════════════════════════════════════════════════════════════ */
 
/* ───────────────────────────────────────────────────────────────────
   CSS VARIABLES — Corporate Color Palette
   ─────────────────────────────────────────────────────────────────── */
 
:root {
  /* Layer Colors */
  --layer-1-bg: #FFE6F0;      /* Light Pink - Data Sources */
  --layer-2-bg: #FFF9E6;      /* Light Yellow - Ingestion */
  --layer-3-bg: #E6F7E6;      /* Light Green - Processing */
  --layer-4-bg: #F0E6FF;      /* Lavender - Storage */
  --layer-5-bg: #FFE9DB;      /* Peach - Analytics */
  --layer-6-bg: #FFE6E6;      /* Light Coral - Intelligence */
  --layer-7-bg: #E6F7E6;      /* Light Green - Presentation */
 
  /* Security & Special Sections */
  --security-bg: #FFEB3B;     /* Bright Yellow */
  --security-border: #F57F17;
  --benefits-bg: #E3F2FD;     /* Soft Blue */
 
  /* Corporate Colors */
  --primary-blue: #0066CC;
  --dark-blue: #003D7A;
  --success-green: #28A745;
  --warning-yellow: #FFC107;
  --danger-red: #DC3545;
 
  /* Neutral Colors */
  --text-primary: #333;
  --text-secondary: #555;
  --text-muted: #666;
  --border-color: #DDD;
  --card-shadow: 0 2px 8px rgba(0,0,0,0.1);
 
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'Courier New', Courier, monospace;
}
 
/* ───────────────────────────────────────────────────────────────────
   GLOBAL RESETS & BASE STYLES
   ─────────────────────────────────────────────────────────────────── */
 
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
 
body {
  font-family: var(--font-family);
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  background: white;
  -webkit-font-smoothing: antialiased;
}
 
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
}
 
/* ───────────────────────────────────────────────────────────────────
   HEADER SECTION
   ─────────────────────────────────────────────────────────────────── */
 
.header {
  background: linear-gradient(135deg, #0066CC 0%, #003D7A 100%);
  color: white;
  padding: 40px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: var(--card-shadow);
}
 
.header-title {
  font-size: 42px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}
 
.header-subtitle {
  font-size: 24px;
  color: rgba(255,255,255,0.9);
  font-weight: 300;
  margin-bottom: 20px;
}
 
.header-meta {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
  margin-top: 20px;
  font-size: 14px;
  color: rgba(255,255,255,0.95);
}
 
.header-meta strong {
  color: white;
  font-weight: 600;
}
 
.status-approved {
  background: var(--success-green);
  color: white;
  padding: 2px 12px;
  border-radius: 12px;
  font-weight: 600;
}
 
.status-approved-conditional {
  background: var(--warning-yellow);
  color: var(--text-primary);
  padding: 2px 12px;
  border-radius: 12px;
  font-weight: 600;
}
 
.status-revision {
  background: var(--danger-red);
  color: white;
  padding: 2px 12px;
  border-radius: 12px;
  font-weight: 600;
}
 
.score-badge {
  background: white;
  color: var(--primary-blue);
  padding: 2px 12px;
  border-radius: 12px;
  font-weight: 700;
}
 
.executive-summary {
  background: rgba(255,255,255,0.15);
  padding: 25px;
  margin-top: 25px;
  border-left: 5px solid white;
  border-radius: 5px;
}
 
.executive-summary h2 {
  font-size: 20px;
  color: white;
  margin-bottom: 12px;
  font-weight: 600;
}
 
.executive-summary p {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255,255,255,0.95);
}
 
/* ───────────────────────────────────────────────────────────────────
   LEGEND SECTION
   ─────────────────────────────────────────────────────────────────── */
 
.legend-section {
  background: #F8F9FA;
  padding: 20px 30px;
  margin: 30px 0;
  border-radius: 5px;
  border: 1px solid var(--border-color);
}
 
.legend-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 15px;
}
 
.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 25px;
}
 
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}
 
.legend-icon {
  font-size: 20px;
  color: var(--primary-blue);
}
 
/* ───────────────────────────────────────────────────────────────────
   LAYER SECTIONS
   ─────────────────────────────────────────────────────────────────── */
 
.layer-section {
  margin: 50px 0;
  padding: 30px;
  border-radius: 8px;
  border: 2px solid var(--border-color);
  box-shadow: var(--card-shadow);
}
 
.layer-1 { background: var(--layer-1-bg); }
.layer-2 { background: var(--layer-2-bg); }
.layer-3 { background: var(--layer-3-bg); }
.layer-4 { background: var(--layer-4-bg); }
.layer-5 { background: var(--layer-5-bg); }
.layer-6 { background: var(--layer-6-bg); }
.layer-7 { background: var(--layer-7-bg); }
 
.layer-header {
  font-size: 20px;
  font-weight: 700;
  color: var(--dark-blue);
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 3px solid var(--primary-blue);
  padding-bottom: 10px;
}
 
.layer-description {
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: 25px;
  font-style: italic;
}
 
.layer-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  grid-auto-rows: 1fr; /* EQUAL HEIGHTS */
}
 
/* ───────────────────────────────────────────────────────────────────
   COMPONENT CARDS
   ─────────────────────────────────────────────────────────────────── */
 
.component-card {
  background: white;
  padding: 20px;
  border-radius: 5px;
  border: 2px solid var(--primary-blue);
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column; /* EQUAL HEIGHTS */
}
 
.component-card h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-bottom: 15px;
  border-bottom: 2px solid var(--primary-blue);
  padding-bottom: 8px;
}
 
.component-card p {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: 12px;
}
 
.component-card strong {
  color: var(--dark-blue);
  font-weight: 600;
}
 
/* ───────────────────────────────────────────────────────────────────
   SECURITY CHECKPOINTS
   ─────────────────────────────────────────────────────────────────── */
 
.security-checkpoint {
  background: var(--security-bg);
  border: 3px solid var(--security-border);
  padding: 20px 30px;
  margin: 30px 0;
  border-radius: 8px;
  text-align: center;
  box-shadow: var(--card-shadow);
}
 
.security-checkpoint h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}
 
.security-details {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}
 
/* ───────────────────────────────────────────────────────────────────
   FLOW CONNECTORS
   ─────────────────────────────────────────────────────────────────── */
 
.flow-connector {
  text-align: center;
  font-size: 40px;
  color: var(--primary-blue);
  margin: 20px 0;
  font-weight: 700;
}
 
/* ───────────────────────────────────────────────────────────────────
   BENEFITS SECTION
   ─────────────────────────────────────────────────────────────────── */
 
.benefits-section {
  background: var(--benefits-bg);
  padding: 40px 30px;
  margin: 50px 0;
  border-radius: 8px;
  border: 2px solid var(--primary-blue);
}
 
.benefits-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--dark-blue);
  text-align: center;
  margin-bottom: 30px;
}
 
.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 25px;
  grid-auto-rows: 1fr; /* EQUAL HEIGHTS */
}
 
.benefit-card {
  background: white;
  padding: 25px;
  border-radius: 5px;
  border: 2px solid var(--primary-blue);
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
}
 
.benefit-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-bottom: 15px;
  border-bottom: 2px solid var(--primary-blue);
  padding-bottom: 10px;
}
 
.benefit-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  flex-grow: 1;
}
 
.benefit-card li {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin: 10px 0;
  padding-left: 25px;
  position: relative;
}
 
.benefit-card li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--success-green);
  font-weight: 700;
  font-size: 16px;
}
 
/* ───────────────────────────────────────────────────────────────────
   BUSINESS OUTCOMES
   ─────────────────────────────────────────────────────────────────── */
 
.outcomes-section {
  background: #F8F9FA;
  padding: 40px 30px;
  margin: 50px 0;
  border-radius: 8px;
  border: 2px solid var(--border-color);
}
 
.outcomes-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--dark-blue);
  text-align: center;
  margin-bottom: 30px;
}
 
.outcomes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 25px;
}
 
.outcome-card {
  background: white;
  padding: 30px 20px;
  border-radius: 8px;
  text-align: center;
  border: 2px solid var(--primary-blue);
  box-shadow: var(--card-shadow);
}
 
.outcome-number {
  font-size: 48px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-bottom: 10px;
}
 
.outcome-label {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}
 
.outcome-card p {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}
 
/* ───────────────────────────────────────────────────────────────────
   IMPLEMENTATION METRICS
   ─────────────────────────────────────────────────────────────────── */
 
.metrics-section {
  background: var(--layer-2-bg);
  padding: 40px 30px;
  margin: 50px 0;
  border-radius: 8px;
  border: 2px solid var(--warning-yellow);
}
 
.metrics-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--dark-blue);
  text-align: center;
  margin-bottom: 30px;
}
 
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
  grid-auto-rows: 1fr; /* EQUAL HEIGHTS */
}
 
.metric-card {
  background: white;
  padding: 20px;
  border-radius: 5px;
  border: 2px solid var(--text-primary);
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
}
 
.metric-card h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary-blue);
  margin-bottom: 15px;
  border-bottom: 2px solid var(--primary-blue);
  padding-bottom: 8px;
}
 
.metric-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  flex-grow: 1;
}
 
.metric-card li {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin: 8px 0;
  padding-left: 20px;
  position: relative;
}
 
.metric-card li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--primary-blue);
  font-weight: 700;
}
 
/* ───────────────────────────────────────────────────────────────────
   COST SUMMARY
   ─────────────────────────────────────────────────────────────────── */
 
.cost-section {
  background: white;
  padding: 40px 30px;
  margin: 50px 0;
  border-radius: 8px;
  border: 2px solid var(--border-color);
  box-shadow: var(--card-shadow);
}
 
.cost-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--dark-blue);
  text-align: center;
  margin-bottom: 30px;
}
 
.cost-breakdown {
  max-width: 900px;
  margin: 0 auto;
}
 
.cost-category {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 20px;
  align-items: center;
}
 
.cost-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
 
.cost-amount {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-blue);
  text-align: right;
}
 
.cost-category p {
  grid-column: 1 / -1;
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 8px;
}
 
.cost-total {
  background: var(--primary-blue);
  color: white;
  padding: 25px;
  margin-top: 20px;
  border-radius: 5px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 20px;
  align-items: center;
}
 
.cost-total .cost-label {
  font-size: 20px;
  color: white;
}
 
.cost-total .cost-amount {
  font-size: 28px;
  color: white;
}
 
/* ───────────────────────────────────────────────────────────────────
   RISK SUMMARY
   ─────────────────────────────────────────────────────────────────── */
 
.risk-section {
  background: white;
  padding: 40px 30px;
  margin: 50px 0;
  border-radius: 8px;
  border: 2px solid var(--border-color);
  box-shadow: var(--card-shadow);
}
 
.risk-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--dark-blue);
  text-align: center;
  margin-bottom: 30px;
}
 
.risk-container {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
 
.risk-item {
  padding: 20px;
  border-radius: 5px;
  border-left: 5px solid;
  box-shadow: var(--card-shadow);
}
 
.risk-high {
  background: #FFEBEE;
  border-color: var(--danger-red);
}
 
.risk-medium {
  background: #FFF8E1;
  border-color: var(--warning-yellow);
}
 
.risk-low {
  background: #E8F5E9;
  border-color: var(--success-green);
}
 
.risk-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}
 
.risk-severity {
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 12px;
  background: white;
}
 
.risk-high .risk-severity {
  color: var(--danger-red);
  border: 2px solid var(--danger-red);
}
 
.risk-medium .risk-severity {
  color: #F57F17;
  border: 2px solid #F57F17;
}
 
.risk-low .risk-severity {
  color: var(--success-green);
  border: 2px solid var(--success-green);
}
 
.risk-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
 
.risk-mitigation {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
  padding-left: 15px;
}
 
/* ───────────────────────────────────────────────────────────────────
   DATA FLOW PATHWAY
   ─────────────────────────────────────────────────────────────────── */
 
.dataflow-section {
  background: #F8F9FA;
  padding: 40px 30px;
  margin: 50px 0;
  border-radius: 8px;
  border: 2px solid var(--border-color);
}
 
.dataflow-section h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--dark-blue);
  text-align: center;
  margin-bottom: 30px;
}
 
.dataflow-content {
  background: white;
  padding: 30px;
  border-radius: 5px;
  border: 1px solid var(--border-color);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
  overflow-x: auto;
}
 
/* ───────────────────────────────────────────────────────────────────
   FOOTER
   ─────────────────────────────────────────────────────────────────── */
 
.document-footer {
  background: linear-gradient(135deg, #003D7A 0%, #0066CC 100%);
  color: white;
  padding: 40px 30px;
  margin-top: 50px;
  border-radius: 8px;
}
 
.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}
 
.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}
 
.footer-grid h4 {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin-bottom: 12px;
}
 
.footer-grid p {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(255,255,255,0.9);
}
 
.footer-divider {
  height: 1px;
  background: rgba(255,255,255,0.3);
  margin: 30px 0;
}
 
.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 13px;
  color: rgba(255,255,255,0.8);
}
 
/* ───────────────────────────────────────────────────────────────────
   PRINT STYLES
   ─────────────────────────────────────────────────────────────────── */
 
@media print {
  body {
    background: white;
  }
 
  .container {
    max-width: 100%;
    padding: 20px;
  }
 
  .layer-section,
  .benefits-section,
  .outcomes-section,
  .metrics-section,
  .cost-section,
  .risk-section,
  .dataflow-section {
    page-break-inside: avoid;
  }
 
  .header {
    background: var(--dark-blue) !important;
    color: white !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
 
  .component-card,
  .benefit-card,
  .metric-card {
    page-break-inside: avoid;
  }
}
 
/* ───────────────────────────────────────────────────────────────────
   RESPONSIVE DESIGN
   ─────────────────────────────────────────────────────────────────── */
 
@media (max-width: 768px) {
  .container {
    padding: 20px;
  }
 
  .header {
    padding: 25px;
  }
 
  .header-title {
    font-size: 28px;
  }
 
  .header-subtitle {
    font-size: 18px;
  }
 
  .layer-cards,
  .benefits-grid,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
 
  .header-meta {
    flex-direction: column;
    gap: 10px;
  }
 
  .outcomes-grid {
    grid-template-columns: 1fr 1fr;
  }
 
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}
 
@media (max-width: 480px) {
  .outcomes-grid {
    grid-template-columns: 1fr;
  }
}
"""
 
 
def get_enterprise_css_minified() -> str:
    """Return minified CSS for production use."""
    css = get_enterprise_css()
    # Basic minification: remove comments and extra whitespace
    lines = []
    in_comment = False
    for line in css.split('\n'):
        stripped = line.strip()
        if '/*' in stripped:
            in_comment = True
        if not in_comment and stripped:
            lines.append(stripped)
        if '*/' in stripped:
            in_comment = False
    return ' '.join(lines)