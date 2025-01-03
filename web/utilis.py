import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import string

class SimpleChatbot:
    def __init__(self, model_path='chatbot_model.pkl'):
        self.model_path = model_path
        self.knowledge_base = []
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            token_pattern=r'\b\w+\b'
        )
        self.tfidf_matrix = None
        # Load the model during initialization
        self.load_model()

    def clean_text(self, text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = ' '.join(text.split())
        return text

    def load_knowledge(self, text_list, save_model=True):
        if isinstance(text_list, list):
            text = ' '.join(text_list)
        else:
            text = text_list

        sentences = re.split(r'[.!?]+', text)
        self.knowledge_base = [self.clean_text(sent) for sent in sentences if sent.strip()]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.knowledge_base)

        if save_model:
            self.save_model()

    def save_model(self):
        try:
            model_data = {
                'knowledge_base': self.knowledge_base,
                'vectorizer_vocabulary': self.vectorizer.vocabulary_,
                'vectorizer_idf': self.vectorizer.idf_,
                'tfidf_matrix': self.tfidf_matrix
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)

                self.knowledge_base = model_data['knowledge_base']
                self.vectorizer = TfidfVectorizer(
                    stop_words='english',
                    lowercase=True,
                    token_pattern=r'\b\w+\b'
                )
                self.vectorizer.vocabulary_ = model_data['vectorizer_vocabulary']
                self.vectorizer.idf_ = model_data['vectorizer_idf']
                self.tfidf_matrix = model_data['tfidf_matrix']
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def get_response(self, query, threshold=0.3):
        cleaned_query = self.clean_text(query)
        query_vector = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        max_similarity = max(similarities)

        if max_similarity < threshold:
            return "I'm sorry, I don't have enough information to answer that question."

        best_response_idx = np.argmax(similarities)
        return self.knowledge_base[best_response_idx]


# Initialize the chatbot as a global variable
chatbot = SimpleChatbot()

def load_qa_data(file_path):
    with open(file_path, 'r') as file:
        qa_pairs = [line.strip() for line in file if line.strip()]
    return qa_pairs