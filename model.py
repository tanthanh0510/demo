import torch
import numpy as np
from PIL import Image
from transformers import VisionEncoderDecoderModel, AutoTokenizer, ViTFeatureExtractor

image_encoder_model = "google/vit-large-patch32-384"
text_decode_model = "NlpHUST/gpt2-vietnamese"
model_path = "checkpoint/"


def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
    outputs = [self.bos_token_id] + token_ids_0 + [self.eos_token_id]
    return outputs


AutoTokenizer.build_inputs_with_special_tokens = build_inputs_with_special_tokens

feature_extractor = ViTFeatureExtractor.from_pretrained(image_encoder_model)
tokenizer = AutoTokenizer.from_pretrained(text_decode_model)
tokenizer.build_inputs_with_special_tokens = build_inputs_with_special_tokens
tokenizer.model_max_length = 128
tokenizer.pad_token = tokenizer.unk_token


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device: ", device)
model = VisionEncoderDecoderModel.from_pretrained(model_path)
model = model.to(device)

def generate_caption(image_paths):
    img = Image.open(image_paths).convert("RGB")
    imageFeature = feature_extractor(img, return_tensors="pt").pixel_values.to(device)
    output_ids = model.generate(imageFeature, max_length=128, num_beams=5, num_return_sequences=5, return_dict_in_generate=True,output_scores=True, eos_token_id=50257)
    sequences = tokenizer.batch_decode(output_ids['sequences'], skip_special_tokens=True)
    p = torch.exp(output_ids['sequences_scores']).cpu().detach().numpy()
    captions = []
    for i in range(5):
        captions.append(
        {
        "Finding": "<br>".join(sequences[i].strip().split("\n")[:-1]),
        "Impression": sequences[i].strip().split("\n")[-1],
        'p': str(p[i])
        }
        )
    return captions
