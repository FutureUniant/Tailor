import os


def init_path(checkpoint_dir, config_dir, size=512, preprocess='crop'):

    sadtalker_paths = {
        "checkpoint": os.path.join(checkpoint_dir, 'SadTalker_V0.0.2_'+str(size)+'.safetensors'),
        }
    use_safetensor = True

    sadtalker_paths['dir_of_BFM_fitting'] = os.path.join(config_dir) # , 'BFM_Fitting'
    sadtalker_paths['audio2pose_yaml_path'] = os.path.join(config_dir, 'auido2pose.yaml')
    sadtalker_paths['audio2exp_yaml_path'] = os.path.join(config_dir, 'auido2exp.yaml')
    sadtalker_paths['use_safetensor'] =  use_safetensor # os.path.join(config_dir, 'auido2exp.yaml')

    if 'full' in preprocess:
        sadtalker_paths['mappingnet_checkpoint'] = os.path.join(checkpoint_dir, 'mapping_00109-model.pth.tar')
        sadtalker_paths['facerender_yaml'] = os.path.join(config_dir, 'facerender_still.yaml')
    else:
        sadtalker_paths['mappingnet_checkpoint'] = os.path.join(checkpoint_dir, 'mapping_00229-model.pth.tar')
        sadtalker_paths['facerender_yaml'] = os.path.join(config_dir, 'facerender.yaml')
    sadtalker_paths["gfpgan"] = os.path.join(os.path.dirname(checkpoint_dir), "gfpgan")
    return sadtalker_paths
