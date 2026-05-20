import html


def render_results(
    media_url,
    media_kind="image",
    guide_sheet_url="",
    guide_sheet_download_url="",
    guide_sheet_name="guide_sheet.pdf"
):
    media_html = (
        f'<img class="guide-media" src="{html.escape(media_url)}" alt="Hoat anh huong dan thoi khen Hmong">'
        if media_kind == "image"
        else (
            '<video class="guide-media" controls autoplay loop muted playsinline>'
            f'<source src="{html.escape(media_url)}" type="{html.escape(media_kind)}">'
            "Trinh duyet khong ho tro hien thi video huong dan."
            "</video>"
        )
    )

    guide_sheet_html = ""
    if guide_sheet_url:
        guide_sheet_html = f"""
          <section class="card guide-sheet-card">
            <div class="guide-sheet-header">
              <div>
                <h2>T&#224;i li&#7879;u h&#432;&#7899;ng d&#7851;n</h2>
              </div>
              <div class="actions">
                <a class="button" href="{html.escape(guide_sheet_url)}" target="_blank" rel="noopener">
                  M&#7903; PDF
                </a>
                <a class="button button-primary" href="{html.escape(guide_sheet_download_url)}" download="{html.escape(guide_sheet_name)}">
                  T&#7843;i PDF h&#432;&#7899;ng d&#7851;n
                </a>
              </div>
            </div>
          </section>
        """

    return f"""
        <section class="card result">
          <div class="result-top">
            <div>
              <p class="eyebrow">K&#7871;t qu&#7843; d&#7921; &#273;o&#225;n</p>
            </div>
          </div>


          <div class="media-layout">
              {media_html}
          </div>
        </section>

        {guide_sheet_html}
        """
