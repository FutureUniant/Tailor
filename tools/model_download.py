from huggingface_hub import snapshot_download
# huggingface_hub.login("HF_TOKEN") # token 从 https://huggingface.co/settings/tokens 获取

snapshot_download(
  repo_id="xmzhu/whisper-tiny-zh",
  local_dir=r"F:\pretrained_model\whisper\ZhihCheng",
  local_dir_use_symlinks=False,
  proxies={"https": "https://hf-mirror.com/"}
)