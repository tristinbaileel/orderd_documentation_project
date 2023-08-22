from pathlib import Path
from git_manager import GitManager
from pygit2 import Blob
from no_instanciable_meta import NoInstanciable

class GitRetrieaver(metaclass=NoInstanciable):
    @staticmethod
    def retrieve_file(file_path: Path) -> str:
        file_git_id = (GitRetrieaver._get_file_git_object(file_path)).oid
        file_git_blob = GitManager.project_repo()[file_git_id]
        file_bytes_data = file_git_blob.data
        file_worked_data = file_bytes_data.decode("utf-8")
        return file_worked_data
    
    @staticmethod
    def _get_file_git_object(file_path: Path) -> Blob:
        path_way = str(file_path).split("\\")
        current_object = GitManager.commit_tree()
        for path in path_way:
            current_object = current_object[path]
        return current_object

