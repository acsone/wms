import datetime

import botocore
import s3fs

env = env  # noqa

today = datetime.today().strftime("%Y-%m-%d")

fs_storage = env.ref("alc_fs_attachment.fs_storage_prod")

fs: s3fs = fs_storage.fs.fs
# get all store_fname from ir_attachment
env.cr.execute(
    "SELECT store_fname FROM ir_attachment where fs_storage_code='fsprod' and store_fname is not null"
)
store_fnames = [i[0].partition("://")[2] for i in env.cr.fetchall()]
print(store_fnames[0])
store_fnames = set(store_fnames)


# here we have a s3fs object
# list all files recursively
def list_all_files(fs_storage, root_path=None):
    if root_path is None:
        root_path = fs_storage.directory_path
    for path in fs.ls(root_path):
        if fs.isdir(path):
            yield from list_all_files(fs_storage, path)
        else:
            # if the file has been created before today we keep it
            # (to avoid to delete a file added after the search in ir_attachment)
            creation_date = fs.info(path)["CreationTime"]
            if creation_date < today:
                yield path.replace(f"{fs_storage.directory_path}/", "")


not_found = []
for file_path in list_all_files(fs_storage):
    if file_path not in store_fnames:
        print(f"File not found: {file_path}")
        not_found.append(file_path)

# for path in not_found get the size
total_size = 0
for path in not_found:
    try:
        size = fs_storage.fs.info(f"{path}")["Size"]
        total_size += size
        print(f"Size of {path} is {size}")
    except botocore.exceptions.ClientError as e:
        print(f"Error getting size of {path}: {e}")
print(f"Total size of files not found: {total_size}")
print(len(not_found))
