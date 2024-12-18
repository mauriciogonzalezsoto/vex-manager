import os

import vex_manager.config as config
import vex_manager.core.file_manager as file_manager


FILE_EXTENSION = '.vfl'


def create_vex_library() -> str:
    home_path = os.path.expanduser('~')
    folder_path = os.path.join(home_path, 'vex-manager-test', config.WrangleNodes.ATTRIB_WRANGLE.value[1])

    for i in range(5):
        vex_file_path = os.path.join(folder_path, f'VEX{i + 1:02}{FILE_EXTENSION}')

        if not os.path.exists(vex_file_path):
            open(vex_file_path, 'a').close()

    return folder_path


def create_new_file() -> None:
    folder_path = create_vex_library()

    # Default name.
    new_vex_file = file_manager.create_new_vex_file(folder_path=folder_path)

    # Custom name.
    new_vex_file_custom_name = file_manager.create_new_vex_file(folder_path=folder_path, name='test')

    print(f'New VEX file {new_vex_file!r}.')
    print(f'New VEX file custom name {new_vex_file_custom_name!r}.')


def delete_file() -> None:
    folder_path = create_vex_library()
    vex_file_path = os.path.join(folder_path, f'VEX01{FILE_EXTENSION}')

    file_manager.delete_file(vex_file_path)


def get_vex_files() -> None:
    folder_path = create_vex_library()
    vex_files = file_manager.get_vex_files(folder_path)

    print(vex_files)


def rename_vex_file() -> None:
    folder_path = create_vex_library()
    vex_file_path = os.path.join(folder_path, f'VEX02{FILE_EXTENSION}')

    file_manager.rename_vex_file(vex_file_path, 'renamed')
    # file_manager.rename_vex_file(vex_file_path, 'VEX02')


if __name__ == '__main__':
    create_new_file()
    delete_file()
    rename_vex_file()
    get_vex_files()
