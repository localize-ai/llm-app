from sentence_transformers import SentenceTransformer
from transformers import CLIPTokenizer

clip_model = SentenceTransformer("clip-ViT-L-14")

clip_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
