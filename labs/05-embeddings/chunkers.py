"""E2 - fixed-size vs paragraph-aware chunking, compared on retrieval hits."""
def fixed(text, size=400, overlap=50):
    return [text[i:i+size] for i in range(0, len(text), size - overlap)]

def paragraphs(text, max_len=600):
    out, buf = [], ""
    for p in text.split("\n\n"):
        if len(buf) + len(p) > max_len and buf:
            out.append(buf.strip()); buf = ""
        buf += p + "\n\n"
    if buf.strip():
        out.append(buf.strip())
    return out
# Exercise: embed both chunkings of the same doc, run your 5 test questions,
# and count which chunker's top-3 actually contains the answer.
