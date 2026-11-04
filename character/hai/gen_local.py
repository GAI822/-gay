"""SDXL-Turbo を CPU で動かして猫の画像を作る（Higgsfield のクレジットが無いときの代替）。
使い方: python3 gen_local.py jobs.json   jobs.json: [{"out": "a.png", "prompt": "...", "seed": 1, "w": 576, "h": 1024}, ...]
1枚あたり約2〜3分（4コアCPU）。"""
import json, sys, time, torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(4)
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16")
pipe.set_progress_bar_config(disable=True)
for j in json.load(open(sys.argv[1])):
    t = time.time()
    img = pipe(prompt=j["prompt"], num_inference_steps=4, guidance_scale=0.0, width=j.get("w", 576), height=j.get("h", 1024),
               generator=torch.Generator().manual_seed(j.get("seed", 0))).images[0]
    img.save(j["out"]); print(j["out"], round(time.time() - t), "s", flush=True)
