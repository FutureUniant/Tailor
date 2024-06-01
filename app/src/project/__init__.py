PROJECT_DB = "project.db"
PROJECT_IMAGE = "project_image.png"
PROJECT_FILEs = "files"
PROJECT_VIDEOS = "videos"
TAILOR_EXTENSION = [".tailor"]

import os
import shutil
import random

from app.utils.paths import Paths
from app.config.app_image import APPIMAGE
from app.src.utils.zipper import Zipper
from app.src.utils.timer import Timer
from app.src.utils.imager import compare_images
from app.utils.version import Version

from app.src.project.model.config import Config
from app.src.project.dao.action_dao import ActionDAO
from app.src.project.dao.config_dao import ConfigDAO
from app.src.project.dao.operation_dao import OperationDAO
from app.src.project.dao.video_dao import VideoDAO


class ProjectUtils:
    """

        The path in project(.tailor) is relative path to the project root path.
    """
    @classmethod
    def new_project(cls, tailor_path):
        project_name = os.path.basename(tailor_path).split(".")[0]

        random_suffix = str(random.randint(0, 9999)).zfill(4)
        unzip_name = f"{Timer.get_format_time()}{random_suffix}"
        unzip_path = os.path.join(Paths.PROJECTFILE, unzip_name)
        os.makedirs(unzip_path, exist_ok=True)

        # create "files" folder and "videos" folder
        files = os.path.join(unzip_path, "files")
        os.makedirs(files, exist_ok=True)
        videos = os.path.join(unzip_path, "videos")
        os.makedirs(videos, exist_ok=True)

        # initial tables
        config_dao = ConfigDAO(unzip_path)
        config_dao.create_config_table(project_name)
        new_project_image_name = APPIMAGE["NEW_PROJECT_PNG"]
        new_project_image = os.path.join(Paths.STATIC, new_project_image_name)
        tailor_image_path = os.path.join(Paths.TAILORFILE, f"{unzip_name}{os.path.splitext(new_project_image)[1]}")
        # copy image to project
        shutil.copy(new_project_image,
                    os.path.join(unzip_path, PROJECT_IMAGE))
        # copy image to tailor
        shutil.copy(new_project_image,
                    os.path.join(Paths.TAILORFILE, tailor_image_path))

        action_dao = ActionDAO(unzip_path)
        action_dao.create_action_table()

        operation_dao = OperationDAO(unzip_path)
        operation_dao.create_operation_table()

        video_dao = VideoDAO(unzip_path)
        video_dao.create_video_table()

        Zipper.compress(tailor_path, unzip_path)
        project_info = {
            "tailor_path": tailor_path,
            "project_path": unzip_path,
            "project_name": project_name,
            "image_path": tailor_image_path,
        }
        return project_info

    @classmethod
    def open_project(cls, tailor_path, **kwargs):
        """

        :param tailor_path:
        :param kwargs
               save:        Save specifically refers to saving project image,
                            which also means opening the project for the first time
               project_image_path:  When the project has been recorded in project_info table,
                                    project_image_path will be not None.
        :return:
        """
        tailor_path = os.path.normpath(tailor_path)
        save = kwargs.get("save", True)
        project_image_path = kwargs.get("project_image_path", None)

        random_suffix = str(random.randint(0, 9999)).zfill(4)
        unzip_name = f"{Timer.get_format_time()}{random_suffix}"
        unzip_path = os.path.join(Paths.PROJECTFILE, unzip_name)
        Zipper.decompress(unzip_path, tailor_path)

        last_open_time = Timer.get_timestamp(integer=True, string=False)
        config_dao = ConfigDAO(unzip_path)
        config = Config(name="last_open_time", value=last_open_time)
        config_dao.update([config])

        config = config_dao.select_by_name("major")[0]
        major = config.value
        config = config_dao.select_by_name("minor")[0]
        minor = config.value
        config = config_dao.select_by_name("patch")[0]
        patch = config.value
        config = config_dao.select_by_name("image_path")[0]
        image_path = config.value

        project_info = {
            "project_path": unzip_path,
            "tailor_path": tailor_path,
            "last_open_time": last_open_time,
            "major": major,
            "minor": minor,
            "patch": patch,
        }
        if project_image_path is not None:
            if os.path.exists(project_image_path):
                compare_flag = compare_images(project_image_path, os.path.join(unzip_path, image_path))
                if compare_flag != 1:
                    save = True
                    if compare_flag == -1:
                        if os.path.exists(project_image_path):
                            os.remove(project_image_path)
                    elif compare_flag == -2:
                        # copy image to project
                        shutil.copy(project_image_path,
                                    os.path.join(unzip_path, image_path))
                    elif compare_flag == -3:
                        new_project_image_name = APPIMAGE["NEW_PROJECT_PNG"]
                        new_project_image = os.path.join(Paths.STATIC, new_project_image_name)
                        # copy image to project
                        shutil.copy(new_project_image,
                                    os.path.join(unzip_path, image_path))

        if save:
            config = config_dao.select_by_name("tailor")[0]
            tailor_name = config.value

            # if first open this tailor project, copy a project image to TAILORFILE
            tailor_image_path = os.path.join(Paths.TAILORFILE, f"{unzip_name}{os.path.splitext(image_path)[1]}")
            shutil.copy(os.path.join(unzip_path, image_path),
                        tailor_image_path)

            project_info["project_name"] = tailor_name
            project_info["image_path"] = tailor_image_path
        return project_info

    @classmethod
    def save_project(cls, project_path, tailor_path):
        update_time = Timer.get_timestamp(integer=True, string=False)
        config_dao = ConfigDAO(project_path)
        config = Config(name="update_time", value=update_time)
        config_dao.update([config])

        Zipper.compress(tailor_path, project_path)

    @classmethod
    def save_as_project(cls, project_path, save_as_tailor_path):
        timestamp = Timer.get_timestamp(integer=True, string=False)
        project_name = os.path.splitext(os.path.basename(save_as_tailor_path))[0]
        configs = [
            Config(name="name", value=project_name),
            Config(name="image_path", value=PROJECT_IMAGE),
            Config(name="create_time", value=timestamp),
            Config(name="update_time", value=timestamp),
            Config(name="last_open_time", value=timestamp),
            Config(name="major", value=Version.major),
            Config(name="minor", value=Version.minor),
            Config(name="patch", value=Version.patch),
        ]
        config_dao = ConfigDAO(project_path)
        config_dao.update(configs)
        Zipper.compress(save_as_tailor_path, project_path)

    @classmethod
    def close_project(cls, project_path):
        shutil.rmtree(project_path)

    @classmethod
    def rename_project(cls, project_path, new_name):
        config_dao = ConfigDAO(project_path)
        config = Config(name="tailor", value=new_name)
        config_dao.update([config])

    @classmethod
    def is_tailor_file(cls, path):
        flag = False
        if (isinstance(path, str) and
                os.path.exists(path) and
                os.path.splitext(path)[1] in TAILOR_EXTENSION):
            flag = True
        return flag




# new_project = ProjectUtils.new_project
# open_project = ProjectUtils.open_project
# save_project = ProjectUtils.save_project
# save_as_project = ProjectUtils.save_as_project

