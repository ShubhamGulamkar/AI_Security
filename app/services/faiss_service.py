import os
import faiss
import pickle
import numpy as np

# OpenAI text-embedding-3-small
DIMENSION = 1536

VECTORSTORE_DIR = "vectorstore"

INDEX_PATH = os.path.join(
    VECTORSTORE_DIR,
    "faiss_index.bin"
)

METADATA_PATH = os.path.join(
    VECTORSTORE_DIR,
    "metadata.pkl"
)

os.makedirs(
    VECTORSTORE_DIR,
    exist_ok=True
)

# -----------------------------
# Load/Create FAISS Index
# -----------------------------

if os.path.exists(INDEX_PATH):

    print("Loading existing FAISS index...")

    index = faiss.read_index(
        INDEX_PATH
    )

else:

    print("Creating new FAISS index...")

    index = faiss.IndexFlatL2(
        DIMENSION
    )

    faiss.write_index(
        index,
        INDEX_PATH
    )

# -----------------------------
# Load Metadata
# -----------------------------

if os.path.exists(METADATA_PATH):

    with open(
        METADATA_PATH,
        "rb"
    ) as f:

        metadata = pickle.load(f)

else:

    metadata = []

# -----------------------------
# Save Metadata
# -----------------------------

def save_metadata():

    with open(
        METADATA_PATH,
        "wb"
    ) as f:

        pickle.dump(
            metadata,
            f
        )

# -----------------------------
# Add Chunk
# -----------------------------

def add_chunk(
    embedding,
    chunk
):

    vector = np.array(
        [embedding],
        dtype=np.float32
    )

    index.add(
        vector
    )

    metadata.append(
        chunk
    )

    faiss.write_index(
        index,
        INDEX_PATH
    )

    save_metadata()

    print(
        f"Chunk Added. Total vectors = {index.ntotal}"
    )

# -----------------------------
# Search Similar Chunks
# -----------------------------

def search(
    embedding,
    top_k=5
):

    if index.ntotal == 0:

        return []

    vector = np.array(
        [embedding],
        dtype=np.float32
    )

    distances, ids = index.search(
        vector,
        top_k
    )

    results = []

    for idx in ids[0]:

        if (
            idx >= 0
            and idx < len(metadata)
        ):

            results.append(
                metadata[idx]
            )

    return results

# -----------------------------
# Get Total Chunks
# -----------------------------

def total_chunks():

    return index.ntotal

# -----------------------------
# Reset Vector Store
# -----------------------------

def reset_vector_store():

    global index
    global metadata

    index = faiss.IndexFlatL2(
        DIMENSION
    )

    metadata = []

    faiss.write_index(
        index,
        INDEX_PATH
    )

    save_metadata()

    print(
        "Vector store reset completed"
    )


# import faiss
# import numpy as np
# import pickle


# DIMENSION = 1536

# # index = faiss.IndexFlatL2(
# #     DIMENSION
# # )
# faiss.write_index(
#     index,
#     "vectorstore/faiss_index.bin"
# )
# index = faiss.read_index(
#     "vectorstore/faiss_index.bin"
# )

# metadata = []


# def add_chunk(
#     embedding,
#     chunk_text
# ):

#     vector = np.array(
#         [embedding],
#         dtype="float32"
#     )

#     index.add(vector)

#     metadata.append(
#         chunk_text
#     )


# def search(
#     embedding,
#     top_k=5
# ):

#     vector = np.array(
#         [embedding],
#         dtype="float32"
#     )

#     distances, ids = index.search(
#         vector,
#         top_k
#     )

#     results = []

#     for idx in ids[0]:

#         if idx < len(metadata):

#             results.append(
#                 metadata[idx]
#             )

#     return results