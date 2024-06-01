import os
import shutil
import zipfile


class Zipper:
    """
        Specialized in handling engineering related decompression/compression parsing.
    """

    # zip
    @classmethod
    def compress(cls, zip_path, file_path, extension=".tailor"):
        # get file name or folder name
        # zip_name = cls.get_file_name(file_path)
        if not zip_path.endswith(extension):
            zip_path = f"{zip_path}{extension}"

        # compress one project
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(file_path):
                # 如果是目录，将目录及其内容压缩到 zip 文件中
                cls.zip_directory(file_path, zipf, file_path)
            else:
                # 如果是文件，直接将文件添加到 zip 文件中
                zipf.write(file_path, arcname=os.path.basename(file_path))

    # 文件夹压缩
    @classmethod
    def zip_directory(cls, file_path, zipf, base_path=""):
        for root, dirs, files in os.walk(file_path):
            # 计算当前文件夹在 ZIP 中的相对路径
            relative_path = os.path.relpath(root, base_path)

            # 忽略根目录
            if relative_path != ".":
                # 添加当前文件夹到 ZIP 文件中
                zipf.write(root, arcname=relative_path)

            # 添加当前文件夹中的所有文件到 ZIP 文件中
            for file in files:
                file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(file_path, base_path)
                zipf.write(file_path, arcname=relative_file_path)

    # get file name. if folder, return folder name
    @classmethod
    def get_file_name(cls, path):
        # whether or not dir
        if os.path.isdir(path):
            return os.path.basename(path)
        base_name = os.path.basename(path)
        return os.path.splitext(base_name)[0]

    # unzip
    @classmethod
    def decompress(cls, unzip_path, file_path):
        unzip_path = cls.create_folders(unzip_path)
        # decompress proeject to folder_path
        with zipfile.ZipFile(file_path, "r", compression=zipfile.ZIP_DEFLATED) as full_zip:
            full_zip.extractall(unzip_path)

    # Create a folder based on the compressed file name and path
    @classmethod
    def create_folders(cls, unzip_path):
        os.makedirs(unzip_path, exist_ok=True)
        return unzip_path

