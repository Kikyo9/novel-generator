"""CSS styles for the book reader component."""


READER_CSS = """
<style>
/* ---- Reader Container ---- */
.reader-wrapper {
    display: flex;
    justify-content: center;
    padding: 20px 0;
}
.reader-book {
    max-width: 720px;
    width: 100%;
    padding: 48px 56px 60px 56px;
    background: #faf6ee;
    color: #2c2416;
    font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", Georgia,
                 "Times New Roman", serif;
    line-height: 2.0;
    box-shadow: 0 2px 16px rgba(0,0,0,0.08),
                0 0 0 1px rgba(0,0,0,0.04);
    border-radius: 2px;
    min-height: 75vh;
    position: relative;
}
.reader-book::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 20px;
    background: linear-gradient(to right,
        rgba(0,0,0,0.03) 0%, rgba(0,0,0,0.01) 40%, transparent 100%);
    border-radius: 2px 0 0 2px;
}
.reader-book .chapter-title {
    font-size: 1.6em;
    font-weight: 700;
    text-align: center;
    margin-bottom: 2em;
    letter-spacing: 0.05em;
}
.reader-book .chapter-content p {
    text-indent: 2em;
    margin: 0.6em 0;
    text-align: justify;
}

/* ---- Night Mode ---- */
.night-mode .reader-book {
    background: #1a1a24;
    color: #c8c8d0;
    box-shadow: 0 2px 16px rgba(0,0,0,0.3),
                0 0 0 1px rgba(255,255,255,0.04);
}
.night-mode .reader-book::before {
    background: linear-gradient(to right,
        rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 40%, transparent 100%);
}

/* ---- Controls Bar ---- */
.reader-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    padding: 12px 16px;
    background: rgba(0,0,0,0.03);
    border-radius: 8px;
    margin-bottom: 20px;
    justify-content: center;
}
.night-mode .reader-controls {
    background: rgba(255,255,255,0.04);
}

/* ---- Progress ---- */
.reader-progress {
    text-align: center;
    font-size: 0.85em;
    color: #999;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(0,0,0,0.06);
}
.night-mode .reader-progress {
    border-top-color: rgba(255,255,255,0.06);
}

/* ---- Step Indicator ---- */
.step-indicator {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 24px;
}
.step-dot {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8em;
    font-weight: 600;
    background: #e8e5df;
    color: #999;
    transition: all 0.3s;
}
.step-dot.active {
    background: #4a4458;
    color: #fff;
}
.step-dot.done {
    background: #8b9a6e;
    color: #fff;
}
.step-line {
    width: 40px;
    height: 2px;
    background: #e8e5df;
    align-self: center;
}
.step-line.done {
    background: #8b9a6e;
}

/* ---- Config Panel ---- */
.config-card {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.config-section-title {
    font-size: 1.05em;
    font-weight: 600;
    color: #4a4458;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 2px solid #f0ede6;
}

/* ---- Outline Editor ---- */
.outline-chapter {
    background: #fff;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border-left: 3px solid #8b9a6e;
}
.outline-chapter .ch-num {
    font-weight: 700;
    color: #4a4458;
    margin-right: 8px;
}

/* ---- Bookshelf ---- */
.book-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    cursor: pointer;
    transition: box-shadow 0.2s;
}
.book-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.book-card .book-title {
    font-size: 1.15em;
    font-weight: 600;
    color: #2c2416;
}
.book-card .book-meta {
    font-size: 0.85em;
    color: #999;
    margin-top: 4px;
}
</style>
"""
