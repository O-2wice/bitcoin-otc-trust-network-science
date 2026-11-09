# LaTeX report

The compiled report is [`report/bitcoin_otc_report.pdf`](../report/bitcoin_otc_report.pdf) (15 pages).

[Download the Overleaf ZIP](bitcoin_otc_report_overleaf.zip). The archive contains `main.tex`, the bibliography, Springer Nature template files, and all seven report figures.

After changing the source, rebuild the PDF in Overleaf or locally. Check that it has 10 to 15 pages; if it runs over, reduce the figure widths in `main.tex`. Then replace `report/bitcoin_otc_report.pdf` with the new PDF.

## Overleaf

1. In Overleaf, choose **New project → Existing project (.zip)** and select the archive.
2. Set the main document to **main.tex** and the compiler to **pdfLaTeX**.
3. Recompile and download the PDF.

[Overleaf upload instructions](https://docs.overleaf.com/managing-projects-and-files/uploading-a-project).

## Locally with MiKTeX or TeX Live

Extract the archive into an empty folder, then run these commands in that folder:

```text
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

MiKTeX downloads missing packages during the first run if its package installation setting is **Always**.
