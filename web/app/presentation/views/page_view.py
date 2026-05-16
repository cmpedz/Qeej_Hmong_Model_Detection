import html

from app.presentation.views.results_view import render_results
from app.shared.formatting import format_milliseconds, format_seconds
from app.shared.media import build_download_url, build_media_url


def render_page(result=None, error_message=""):
    error_html = ""
    if error_message:
        error_html = (
            "<section class='card error'>"
            "<h2>Lỗi: </h2>"
            f"<p>{html.escape(error_message)}</p>"
            "</section>"
        )

    result_html = ""
    if result is not None:
        media_url = build_media_url(result.guide_media_path)
        guide_sheet_url = build_media_url(result.guide_sheet_path)
        guide_sheet_download_url = build_download_url(result.guide_sheet_path, result.guide_sheet_path.name)
        media_kind = "image"
        if result.guide_media_path.suffix.lower() in {".mp4", ".webm"}:
            media_kind = f"video/{result.guide_media_path.suffix.lower().lstrip('.')}"
        timing_cards = "".join(
            f"<div class='metric'><span>{html.escape(label)}</span><strong>{html.escape(format_milliseconds(value))}</strong></div>"
            for label, value in result.timings_ms.items()
        )
        metrics_html = (
            "<div class='result-grid'>"
            f"<div class='metric'><span>Audio length</span><strong>{html.escape(format_seconds(result.duration_seconds))}s</strong></div>"
            f"<div class='metric'><span>Total windows</span><strong>{result.total_windows}</strong></div>"
            f"<div class='metric'><span>Predict workers</span><strong>{result.predict_workers}</strong></div>"
            f"{timing_cards}"
            "</div>"
        )
        result_html = render_results(
            media_url,
            media_kind=media_kind,
            guide_sheet_url=guide_sheet_url,
            guide_sheet_download_url=guide_sheet_download_url,
            guide_sheet_name=result.guide_sheet_path.name,
            metrics_html=metrics_html,
        )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MKQH Qeej Guide</title>
  <style>
    :root {{
      --bg: #f3ede3;
      --ink: #1f1b16;
      --muted: #65594e;
      --card: rgba(255, 251, 246, 0.88);
      --line: rgba(72, 52, 33, 0.12);
      --accent: #9f4b24;
      --accent-2: #d9894b;
      --ok: #214f39;
      --error: #8a2d1d;
      --shadow: 0 24px 60px rgba(76, 48, 24, 0.12);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Aptos", "Trebuchet MS", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(217, 137, 75, 0.22), transparent 28%),
        radial-gradient(circle at bottom right, rgba(159, 75, 36, 0.18), transparent 30%),
        linear-gradient(160deg, #f7f1e8 0%, #efe1cd 100%);
      min-height: 100vh;
    }}
    .shell {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 40px 20px 64px;
    }}
    .hero {{
      padding: 28px;
      border-radius: 28px;
      background:
        linear-gradient(135deg, rgba(31, 27, 22, 0.95), rgba(69, 43, 23, 0.88)),
        linear-gradient(135deg, rgba(217, 137, 75, 0.2), rgba(255, 255, 255, 0));
      color: #fff9f3;
      box-shadow: var(--shadow);
      overflow: hidden;
      position: relative;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -8% -40% auto;
      width: 240px;
      height: 240px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(217, 137, 75, 0.3), transparent 70%);
      pointer-events: none;
    }}
    .eyebrow {{
      margin: 0 0 8px;
      color: #f3c89d;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-size: 0.76rem;
      font-weight: 700;
    }}
    h1 {{
      margin: 0 0 14px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(2rem, 5vw, 3.4rem);
      line-height: 1.05;
    }}
    .hero p {{
      margin: 0;
      max-width: 720px;
      color: rgba(255, 249, 243, 0.9);
      line-height: 1.65;
      font-size: 1rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-top: 22px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--card);
      backdrop-filter: blur(8px);
      box-shadow: var(--shadow);
      padding: 24px;
    }}
    .card h2 {{
      margin: 0 0 8px;
      font-size: 1.25rem;
    }}
    .card p {{
      color: var(--muted);
      line-height: 1.6;
    }}
    form {{
      display: grid;
      gap: 16px;
    }}
    label {{
      display: grid;
      gap: 8px;
      font-weight: 700;
    }}
    input[type="file"],
    input[type="number"] {{
      width: 100%;
      border: 1px solid rgba(109, 80, 49, 0.2);
      border-radius: 16px;
      padding: 14px 16px;
      background: rgba(255, 255, 255, 0.84);
      font: inherit;
      color: var(--ink);
    }}
    .hint {{
      margin: 0;
      color: var(--muted);
      font-size: 0.94rem;
    }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border-radius: 999px;
      padding: 12px 18px;
      border: 1px solid rgba(122, 71, 34, 0.2);
      background: rgba(255, 255, 255, 0.72);
      color: var(--ink);
      text-decoration: none;
      font-weight: 700;
      cursor: pointer;
      transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }}
    .button:hover {{
      transform: translateY(-1px);
      box-shadow: 0 12px 28px rgba(74, 45, 21, 0.12);
      background: rgba(255, 255, 255, 0.9);
    }}
    .button-primary {{
      border-color: transparent;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      color: white;
    }}
    .error {{
      border-color: rgba(138, 45, 29, 0.18);
    }}
    .error h2 {{
      color: var(--error);
    }}
    .result-top {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      flex-wrap: wrap;
    }}
    .result .meta {{
      margin-top: 6px;
      font-size: 0.95rem;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 10px 16px;
      background: rgba(255, 248, 237, 0.9);
      color: var(--accent);
      font-weight: 700;
      border: 1px solid rgba(159, 75, 36, 0.18);
    }}
    .media-card {{
      margin: 22px 0;
      padding: 12px;
      border-radius: 24px;
      background: rgba(255, 255, 255, 0.64);
      border: 1px solid rgba(104, 77, 47, 0.12);
    }}
    .media-layout {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 18px;
      align-items: start;
      margin-top: 22px;
    }}
    .guide-media {{
      display: block;
      width: 100%;
      border-radius: 18px;
      border: 1px solid rgba(104, 77, 47, 0.12);
      background: #f5ead8;
    }}
    .download-card {{
      margin: 22px 0;
      padding: 22px;
      border-radius: 24px;
      background: linear-gradient(180deg, rgba(255, 250, 244, 0.96), rgba(249, 238, 220, 0.9));
      border: 1px solid rgba(159, 75, 36, 0.16);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
    }}
    .download-card h2 {{
      margin: 0 0 12px;
    }}
    .download-card p {{
      margin: 0 0 18px;
    }}
    .download-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .guide-sheet-card {{
      margin-top: 22px;
    }}
    .guide-sheet-header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }}
    .guide-sheet-header h2 {{
      margin: 0;
    }}
    .result-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin: 22px 0;
    }}
    .metric {{
      padding: 16px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(104, 77, 47, 0.12);
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 0.88rem;
      margin-bottom: 6px;
    }}
    .metric strong {{
      font-size: 1.12rem;
      color: var(--ok);
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 480px;
    }}
    th, td {{
      padding: 14px 12px;
      border-bottom: 1px solid rgba(100, 73, 43, 0.12);
      text-align: left;
    }}
    th {{
      font-size: 0.88rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
    }}
    .footer-note {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    @media (max-width: 720px) {{
      .shell {{
        padding: 24px 16px 40px;
      }}
      .hero,
      .card {{
        border-radius: 22px;
      }}
      .media-layout {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Kawm Qeej Hmong</p>
      <h1>Trang web hỗ trợ học khèn</h1>
    </section>

    <div class="grid">
      <section class="card">
        <p>Hãy tải file âm thanh định dạng WAV về giai điệu khèn mà bạn đang muốn học, 
        trang web này sẽ cung cấp video hướng dẫn và bản ghi để hỗ trợ bạn luyện tập.</p>
        <form action="/predict" method="post" enctype="multipart/form-data">
          <label>
            Giai điệu của khèn
            <input type="file" name="audio" accept=".wav,audio/wav,audio/x-wav" required>
          </label>

          <button class="button button-primary" type="submit">Tạo video và tài liệu hướng dẫn</button>
        </form>
      </section>

    </div>

    {error_html}
    {result_html}
  </main>
</body>
</html>
"""
