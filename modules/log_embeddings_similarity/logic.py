import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# OPTIONAL: Uncomment this section if you want to connect to a PostgreSQL database on AWS
# import psycopg2

# ✅ Step 1: Set your OpenAI API key
load_dotenv()
api_key = os.getenv("OPEN_AI_API_KEY")
openai.api_key = api_key

# ✅ Step 2: Define a list of chunks (e.g., log entries, paragraphs, etc.)
'''
📌 Reminders: 
* This is preproccesing step so later make a fork and edit so DB will only take new logs and solutions
* In order to maximize the use of the LogEmbedder, insert only failiure logs with there solution. 
Every debugged log should be added to the DB with solution 

* This example uses simple log messages as chunks.
If using a text file or PDF, you'd split it into chunks using:
from langchain.text_splitter import RecursiveCharacterTextSplitter
'''
chunks = [
    "User clicked button but nothing happened",
    "Connection timeout while calling API",
    "Missing field 'username' in request body",
    "Cannot connect to database at 10.0.1.7",
    "Service returned 500 internal server error",
    "Failed to load user profile from backend",
    "Password field is empty in form submission"
]

# OPTIONAL: Connect to AWS PostgreSQL and fetch chunks instead of hardcoding
"""
# 🔁 Uncomment this block to pull chunks from PostgreSQL (AWS RDS)
connection = psycopg2.connect(
    host="your-db-host.amazonaws.com",
    port=5432,
    user="your-username",
    password="your-password",
    dbname="your-database"
)
cursor = connection.cursor()
cursor.execute("SELECT chunk_text FROM logs_table")
chunks = [row[0] for row in cursor.fetchall()]
"""

# ✅ Step 3: Generate embeddings for all chunks (batch mode)
embedding_response = openai.embeddings.create(
    input=chunks,
    model="text-embedding-3-small"
)

# Extract vectors
chunk_vectors = [item.embedding for item in embedding_response.data]

# OPTIONAL: Store embeddings to DB if needed
"""
# 🔁 Uncomment this block to store embeddings into the DB
cursor.execute("DELETE FROM chunk_embeddings")  # optional: clear existing
for i, vector in enumerate(chunk_vectors):
    cursor.execute(
        "INSERT INTO chunk_embeddings (chunk_text, embedding) VALUES (%s, %s)",
        (chunks[i], vector)
    )
connection.commit()
"""

# ✅ Step 4: Define a new input to compare against existing chunks
chunk_to_compare = input("Enter a log to compare: ")
#chunk_to_compare = "Database connection refused"

# Embed the new input chunk
compare_embedding = openai.embeddings.create(
    input=chunk_to_compare,
    model="text-embedding-3-small"
).data[0].embedding

# ✅ Step 5: Compute cosine similarity
query_vector = np.array(compare_embedding).reshape(1, -1)
chunk_matrix = np.array(chunk_vectors)
similarities = cosine_similarity(query_vector, chunk_matrix)[0]

# ✅ Step 6: Get top 3 most similar chunks
top_k = np.argsort(similarities)[::-1][:3]

# ✅ Step 7: Print results
print("📋 Top similar chunks:")
for i in top_k:
    print(f"• Similar chunk: \"{chunks[i]}\"  |  Similarity Score: {similarities[i]:.2f}")

# OPTIONAL: Close DB connection if used
"""
cursor.close()
connection.close()
"""

