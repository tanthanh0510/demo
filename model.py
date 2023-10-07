import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, AutoTokenizer, ViTFeatureExtractor

image_encoder_model = "google/vit-large-patch32-384"
text_decode_model = "NlpHUST/gpt2-vietnamese"
model_path = "checkpoint/checkpoint-7700"


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
model = VisionEncoderDecoderModel.from_pretrained(model_path)


def generate_caption(image_paths):
    img = Image.open(image_paths).convert("RGB")
    caption = tokenizer.decode(model.generate(feature_extractor(
        img, return_tensors="pt").pixel_values.to(device))[0], skip_special_tokens=True)
    caption[:caption.find("\n\n")] if caption.find("\n\n") != -1 else caption
    return caption
