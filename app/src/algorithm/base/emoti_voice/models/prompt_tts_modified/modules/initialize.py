"""
This code is modified from https://github.com/espnet/espnet.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


def initialize(model: torch.nn.Module, init: str):
    for p in model.parameters():
        if p.dim() > 1:
            if init == "xavier_uniform":
                torch.nn.init.xavier_uniform_(p.data)
            elif init == "xavier_normal":
                torch.nn.init.xavier_normal_(p.data)
            elif init == "kaiming_uniform":
                torch.nn.init.kaiming_uniform_(p.data, nonlinearity="relu")
            elif init == "kaiming_normal":
                torch.nn.init.kaiming_normal_(p.data, nonlinearity="relu")
            else:
                raise ValueError("Unknown initialization: " + init)
    # bias init
    for p in model.parameters():
        if p.dim() == 1:
            p.data.zero_()

    # reset some modules with default init
    for m in model.modules():
        if isinstance(
            m, (torch.nn.Embedding, torch.nn.LayerNorm, torch.nn.GroupNorm)
        ):
            m.reset_parameters()
        if hasattr(m, "espnet_initialization_fn"):
            m.espnet_initialization_fn()

    # TODO(xkc): Hacking s3prl_frontend and wav2vec2encoder initialization
    if getattr(model, "encoder", None) and getattr(
        model.encoder, "reload_pretrained_parameters", None
    ):
        model.encoder.reload_pretrained_parameters()
    if getattr(model, "frontend", None) and getattr(
        model.frontend, "reload_pretrained_parameters", None
    ):
        model.frontend.reload_pretrained_parameters()
    if getattr(model, "postencoder", None) and getattr(
        model.postencoder, "reload_pretrained_parameters", None
    ):
        model.postencoder.reload_pretrained_parameters()