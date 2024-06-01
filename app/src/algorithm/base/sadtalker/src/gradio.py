import torch, uuid
import os, sys, shutil
from app.src.algorithm.base.sadtalker.src.utils.preprocess import CropAndExtract
from app.src.algorithm.base.sadtalker.src.test_audio2coeff import Audio2Coeff
from app.src.algorithm.base.sadtalker.src.facerender.animate import AnimateFromCoeff
from app.src.algorithm.base.sadtalker.src.generate_batch import get_data
from app.src.algorithm.base.sadtalker.src.generate_facerender_batch import get_facerender_data

from app.src.algorithm.base.sadtalker.src.utils.init_path import init_path

from pydub import AudioSegment


def mp3_to_wav(mp3_filename, wav_filename, frame_rate):
    mp3_file = AudioSegment.from_file(file=mp3_filename)
    mp3_file.set_frame_rate(frame_rate).export(wav_filename, format="wav")


class SadTalker():

    def __init__(self, checkpoint_path='checkpoints', config_path='src/config', device="cuda"):

        if not torch.cuda.is_available():
            device = "cpu"

        self.device = device

        self.checkpoint_path = checkpoint_path
        self.config_path = config_path
      
    def test(self,
             source_image,
             driven_audio,
             preprocess='crop',
             still_mode=False,
             use_enhancer=False,
             batch_size=1,
             size=256,
             pose_style=0,
             result_dir='./results/'):

        self.sadtalker_paths = init_path(self.checkpoint_path, self.config_path, size, preprocess)

        self.audio_to_coeff = Audio2Coeff(self.sadtalker_paths, self.device)
        self.preprocess_model = CropAndExtract(self.sadtalker_paths, self.device)
        self.animate_from_coeff = AnimateFromCoeff(self.sadtalker_paths, self.device)

        os.makedirs(result_dir, exist_ok=True)

        input_dir = os.path.join(result_dir, 'input')
        os.makedirs(input_dir, exist_ok=True)

        pic_path = os.path.join(input_dir, os.path.basename(source_image))
        shutil.copy(source_image, input_dir)

        if os.path.isfile(driven_audio):
            audio_path = os.path.join(input_dir, os.path.basename(driven_audio))  

            #### mp3 to wav
            if audio_path.endswith('.mp3'):
                mp3_to_wav(driven_audio, audio_path.replace('.mp3', '.wav'), 16000)
                audio_path = audio_path.replace('.mp3', '.wav')
            else:
                shutil.copy(driven_audio, input_dir)
        else:
            raise AttributeError("error audio")

        # crop image and extract 3dmm from image
        first_frame_dir = os.path.join(result_dir, 'first_frame_dir')
        os.makedirs(first_frame_dir, exist_ok=True)
        first_coeff_path, crop_pic_path, crop_info = self.preprocess_model.generate(pic_path, first_frame_dir, preprocess, True, size)
        
        if first_coeff_path is None:
            raise AttributeError("No face is detected")

        #audio2ceoff
        batch = get_data(first_coeff_path, audio_path, self.device, ref_eyeblink_coeff_path=None, still=still_mode)  # longer audio?
        coeff_path = self.audio_to_coeff.generate(batch, result_dir, pose_style)
        #coeff2video
        data = get_facerender_data(coeff_path, crop_pic_path, first_coeff_path, audio_path, batch_size, still_mode=still_mode, preprocess=preprocess, size=size)
        return_path = self.animate_from_coeff.generate(data, result_dir,  pic_path, crop_info, enhancer='gfpgan' if use_enhancer else None, preprocess=preprocess, img_size=size)

        del self.preprocess_model
        del self.audio_to_coeff
        del self.animate_from_coeff

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        import gc; gc.collect()
        
        return return_path

    