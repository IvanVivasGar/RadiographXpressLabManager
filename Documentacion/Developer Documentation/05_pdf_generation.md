# PDF Generation (WeasyPrint) 📄

RadiographXpress generates high-fidelity, printable PDF documents of the radiological reports. The core of this functionality lies in **WeasyPrint**, a visual rendering engine for HTML and CSS that outputs PDF.

## 1. How It Works

Unlike pure programmatic PDF builders (like ReportLab) which require placing text at exact `(x, y)` coordinates, WeasyPrint takes standard web technologies (HTML strings, CSS files, images) and renders them exactly as a modern browser would for printing.

The workflow:
1.  **Context Assembly:** The Django view (`download_report_pdf` or `download_study_report`) gathers the `Study`, `Report`, `Patient`, and `ReportingDoctor` data.
2.  **HTML Rendering:** It passes that context to a standard Django template (e.g., `core/study_report_detail.html`). `render_to_string` creates a pure HTML string.
3.  **Asset Loading:** The system loads a pre-defined CSS string (often hardcoded in the view to avoid Docker relative path complexities for static files).
4.  **PDF Compilation:** `weasyprint.HTML(string=html_string).write_pdf(...)` weaves the HTML, the CSS, and remote images (like S3 profile pictures or doctor signatures) into a binary PDF buffer.
5.  **Response:** The buffer is sent back to the browser with `Content-Type: application/pdf`.

## 2. Core PDF Layout (`core/views.py`)

Here is an example structure of how it is implemented in the views:

```python
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from io import BytesIO

def download_report(request, study_id):
    # 1. Get Context
    study = get_object_or_404(Study, id=study_id)
    
    # 2. Render Template
    html_string = render_to_string('core/study_report_detail.html', {'study': study})
    
    # 3. Define the Global Styles
    css = CSS(string='''
        @page {
            size: letter;
            margin: 0; 
        }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-image: url('http://example.com/background.jpg');
            background-size: cover;
        }
    ''')

    # 4. Generate
    pdf_file = BytesIO()
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        pdf_file,
        stylesheets=[css],
        presentational_hints=True
    )
```

## 3. Important Development Rules

### CSS Support and `@page`
WeasyPrint does not support 100% of modern CSS (e.g., advanced Flexbox, CSS Grid might behave weirdly across page breaks). It is highly reliant on **CSS Paged Media Module** (`@page`).
*   Always define `@page { size: letter; }`.
*   Margins inside `@page` dictate the physical white border of the printed paper.

### Remote Images (S3 & Relative Paths)
WeasyPrint must download all `<img>` tags to embed them. 
*   **Signatures & Logos:** Since media images are stored in AWS S3, passing `base_url=request.build_absolute_uri()` is critical. It tells WeasyPrint how to resolve relative URLs into full HTTPS paths.
*   **Background Images:** If a background image is large, it takes longer to generate the PDF. RadiographXpress uses absolute URLs to load corporate letterheads.

### Handling Page Breaks
A common issue in PDF generation is text splitting across two pages inappropriately (e.g., cutting a signature block in half). Use CSS properties inside your Django template:

```css
.signature-block {
    page-break-inside: avoid;
}
```
This forces WeasyPrint to move the entire block to the next page instead of printing half of it on page 1.
