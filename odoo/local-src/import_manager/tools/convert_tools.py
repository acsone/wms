import shutil
import cchardet


def convert_to_uft_8(file_path):
    with open(file_path, 'rb') as f:
        msg = f.read()
        result = cchardet.detect(msg)
        encoding = result.get('encoding')

        if encoding == 'ASCII':
            return

        if not encoding:
            raise Exception('Cannot retrieve the file encoding')

        encoded_msg = msg.decode(encoding)

    backup_file_path = file_path + '.bak'
    shutil.copy(file_path, backup_file_path)

    with open(file_path, 'wb') as f:
        f.write(encoded_msg.encode('utf-8'))
