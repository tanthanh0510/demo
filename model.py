import torch
import torchvision
from PIL import Image
from transformers import (
    VisionEncoderDecoderModel,
    AutoTokenizer,
    ViTFeatureExtractor
)

from unet import PretrainedUNet
from utils import blend

image_encoder_model = "google/vit-large-patch32-384"
text_decode_model = "NlpHUST/gpt2-vietnamese"
model_path = "checkpoint/"
unetPath = "checkpoint/unet-6v.pt"

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
model.eval()

unet = PretrainedUNet(
    in_channels=1,
    out_channels=2, 
    batch_norm=True, 
    upscale_mode="bilinear"
)

unet.load_state_dict(torch.load(unetPath, map_location=torch.device(device)))
unet.to(device)
unet.eval()

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

def segment(image_path):
    origin = Image.open(image_path).convert("P")
    origin = torchvision.transforms.functional.resize(origin, (512, 512))
    origin = torchvision.transforms.functional.to_tensor(origin) - 0.5
    with torch.no_grad():
        origin = torch.stack([origin])
        origin = origin.to(device)
        out = unet(origin)
        softmax = torch.nn.functional.log_softmax(out, dim=1)
        out = torch.argmax(softmax, dim=1)
        
        origin = origin[0].to("cpu")
        out = out[0].to("cpu")
    img = blend(origin, out)
    return img
