"""EPUB file generation for novels."""
import io

EPUB_AVAILABLE = True
try:
    from ebooklib import epub
except ImportError:
    EPUB_AVAILABLE = False


def is_epub_available() -> bool:
    return EPUB_AVAILABLE


def generate_epub(title: str, author: str, chapters: list,
                  synopsis: str = "") -> bytes:
    """
    Generate an EPUB file from novel chapters.
    Returns empty bytes if ebooklib is not installed.
    """
    if not EPUB_AVAILABLE:
        raise ImportError("ebooklib is not installed. EPUB generation unavailable.")

    book = epub.EpubBook()

    book.set_identifier("novel-gen-workshop")
    book.set_title(title)
    book.set_language("zh")
    book.add_author(author)
    if synopsis:
        book.add_metadata("DC", "description", synopsis)

    style = """
    body { font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif;
           line-height: 1.8; margin: 5%; }
    h1 { text-align: center; font-size: 1.5em; margin: 2em 0 1em 0; }
    p { text-indent: 2em; margin: 0.5em 0; }
    """
    css = epub.EpubItem(uid="style", file_name="style/default.css",
                        media_type="text/css", content=style.encode("utf-8"))
    book.add_item(css)

    spine = ["nav"]
    toc = []
    epub_chapters = []

    for i, ch in enumerate(chapters):
        ch_num = ch.get("number", i + 1)
        ch_title = ch.get("title", f"第{ch_num}章")
        ch_content = ch.get("content", "")

        paragraphs = ch_content.strip().split("\n")
        html_paragraphs = "".join(f"<p>{p}</p>" for p in paragraphs if p.strip())

        chapter_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">
<head><title>{ch_title}</title><link rel="stylesheet" type="text/css" href="style/default.css"/></head>
<body>
<h1>{ch_title}</h1>
{html_paragraphs}
</body>
</html>"""

        file_name = f"chapter_{ch_num}.xhtml"
        epub_chapter = epub.EpubHtml(title=ch_title, file_name=file_name, lang="zh")
        epub_chapter.content = chapter_html.encode("utf-8")
        epub_chapter.add_item(css)

        book.add_item(epub_chapter)
        epub_chapters.append(epub_chapter)
        spine.append(epub_chapter)
        toc.append(epub.Link(file_name, ch_title, f"ch{ch_num}"))

    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    buf = io.BytesIO()
    epub.write_epub(buf, book)
    return buf.getvalue()
