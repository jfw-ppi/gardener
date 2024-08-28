# embed.py

import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry
from sklearn.metrics.pairwise import cosine_similarity


class BGEModelClient:
    def __init__(self, api_url, timeout=10, retries=3):
        self.api_url = api_url
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=retries, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def create_embedding(self, text, normalize=True, truncate=False, truncation_direction="Right"):
        payload = {
            "inputs": text,
            "normalize": normalize,
            "truncate": truncate,
            "truncation_direction": truncation_direction
        }
        try:
            response = self.session.post(f"{self.api_url}/embed", json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()[0]  # Return the first embedding vector
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def create_embeddings_for_df(self, df, column_names, batch_size=10):
        embeddings = []
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            batch_embeddings = []
            for _, row in batch.iterrows():
                text_to_embed = " ".join(str(row[col]) for col in column_names if pd.notna(row[col]))
                embedding = self.create_embedding(text_to_embed)
                batch_embeddings.append(embedding)

            for j, embedding in enumerate(batch_embeddings):
                if embedding is not None:
                    embeddings.append(embedding)
                else:
                    embeddings.append([None] * 1024)  # Assuming 1024 is the embedding size

        df['Embedding'] = embeddings
        return df

    def find_similar_plants(self, input_data, df, column_names, top_n=5, exclude_name=None):
        input_text = " ".join(
            str(input_data[col]) for col in column_names if col in input_data and input_data[col] is not None)
        input_embedding = self.create_embedding(input_text)
        if input_embedding is None:
            return pd.DataFrame()  # Return an empty DataFrame if embedding failed

        df['Similarity'] = df['Embedding'].apply(
            lambda x: cosine_similarity([input_embedding], [x])[0][0] if x is not None else -1)

        if exclude_name:
            df = df[df['ScientificName'] != exclude_name]

        similar_plants = df.sort_values(by='Similarity', ascending=False).head(top_n)
        return similar_plants

    def find_similar_plants_by_scientific_name(self, scientific_name, df, numerical_fields, text_fields, top_n=5):
        plant_data = df[df['ScientificName'] == scientific_name]
        if plant_data.empty:
            print(f"Plant with ScientificName '{scientific_name}' not found.")
            return pd.DataFrame()

        input_data = plant_data.iloc[0][numerical_fields + text_fields].to_dict()

        similar_plants = self.find_similar_plants(input_data, df, numerical_fields + text_fields, top_n,
                                                  exclude_name=scientific_name)
        return similar_plants

# Load the cleaned EcoCrop dataset during initialization
file_path = "resources/Cleaned_EcoCrop_DB_Final.xlsx"
ecocrop_df = pd.read_excel(file_path)

# Fields to use for embedding
text_fields = ["COMNAME", "LIFO", "HABI", "LISPA", "PHYS", "CAT", "LIOPMN"]
numerical_fields = []

# Initialize the BGEModelClient with the API endpoint
bge_client = BGEModelClient(api_url="https://bge-m3.models.th-luebeck.dev")

# Create embeddings for the selected columns (both numerical and text fields)
ecocrop_df = bge_client.create_embeddings_for_df(ecocrop_df, text_fields, batch_size=10)
