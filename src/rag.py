from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_DIR = Path("knowledge-base")

def load_documents():
    documents = []

    for file_path in KB_DIR.rglob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": str(file_path),
            "content": content
        })

    return documents

def chunk_document(document):
    content = document["content"]

    sections = re.split(r"\n---\n", content)

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        headings = re.findall(r"^#{1,6}\s+(.+)$", section, re.MULTILINE)

        section_name = headings[-1] if headings else "General"

        chunks.append({
            "source": document["source"],
            "section": section_name,
            "content": section
        })

    return chunks


def build_retriever(chunks):
    texts = [chunk["content"] for chunk in chunks]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(texts)

    return vectorizer, matrix

def search_knowledge_base(
    query,
    chunks,
    vectorizer,
    matrix,
    top_k=3,
    product=None,
    min_score=0.05,
):
    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(query_vector, matrix).flatten()

    query_upper = query.upper()

    # Extract technical error codes such as:
    # CHECKSUM_MISMATCH
    # AUTH_TOKEN_EXPIRED
    # RATE_LIMIT_EXCEEDED
    error_codes = re.findall(
        r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b",
        query_upper,
    )

    for index, chunk in enumerate(chunks):
        content_upper = chunk["content"].upper()

        # Strong boost only when the exact error code
        # and the product both match.
        for error_code in error_codes:
            if error_code in content_upper:
                if product:
                    product_name = (
                        product.lower()
                        .replace(" ", "")
                        .replace("-", "")
                        )
                    
                    source_name = (
                        chunk["source"]
                        .split("/")[-1]
                        .replace(".md", "")
                        .replace(" ", "")
                        .replace("-", "")
                        .lower()
                        )

                    if product_name == source_name:
                        scores[index] += 0.50

        # Boost matching product documentation.
        if product:
            product_name = (
                product.lower()
                .replace(" ", "")
                .replace("-", "")
            )

            source_name = (
                chunk["source"]
                .split("/")[-1]
                .replace(".md", "")
                .replace(" ", "")
                .replace("-", "")
                .lower()
            )

            if product_name == source_name:
                scores[index] += 0.20

    ranked_indices = scores.argsort()[::-1]

    results = []

    for index in ranked_indices:
        score = float(scores[index])

        if score < min_score:
            continue

        results.append({
            "source": chunks[index]["source"],
            "section": chunks[index]["section"],
            "content": chunks[index]["content"],
            "score": score,
        })

        if len(results) >= top_k:
            break

    return results

if __name__ == "__main__":
    documents = load_documents()

    all_chunks = []

    for document in documents:
        chunks = chunk_document(document)
        all_chunks.extend(chunks)

    vectorizer, matrix = build_retriever(all_chunks)

    query = """
    CloudSync new users cannot authenticate through SSO.
    Existing users can login but new joiners cannot.
    """

    results = search_knowledge_base(
    query,
    all_chunks,
    vectorizer,
    matrix,
    top_k=3,
    product="CloudSync"
)

    print("Query:")
    print(query)

    print("\nTop KB Results:\n")

    for result in results:
        print("SOURCE:", result["source"])
        print("SECTION:", result["section"])
        print("SCORE:", round(result["score"], 3))
        print("CONTENT:")
        print(result["content"][:500])
        print("-" * 70)