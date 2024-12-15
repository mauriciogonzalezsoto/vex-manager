from pathlib import Path
import logging
import glob
import re
import os


import vex_manager.utils as utils


logger = logging.getLogger(f'vex_manager.{__name__}')


def create_new_vex_file(folder_path: str) -> tuple[str, str]:
    library_path = os.path.dirname(folder_path)

    if not os.path.exists(library_path):
        logger.error(f'Library path {library_path!r} does not exist.')
        return '', ''

    files = glob.glob(f'{folder_path}/*.vfl')
    files.sort(reverse=True)

    value = 1

    for file in files:
        base_name = os.path.basename(file)
        match = re.search(r'VEX(\d{2}).vfl', base_name)

        if match:
            current_value = int(match.group(1))

            if value <= current_value:
                value = current_value + 1

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

        logger.info(f'{folder_path!r} folder created.')

    new_vex_file_path = os.path.join(folder_path, f'VEX{value:02d}.vfl')
    base_name = Path(new_vex_file_path).stem

    if not os.path.exists(new_vex_file_path):
        open(new_vex_file_path, 'w').close()

        logger.debug(f'{new_vex_file_path!r} created.')

    return new_vex_file_path, base_name


def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)

        logger.debug(f'{file_path!r} deleted.')
    else:
        logger.error(f'{file_path!r} does not exit.')


def get_vex_files(folder_path: str) -> list[tuple[str, str]]:
    vex_files = []

    if os.path.exists(folder_path):
        for vex_file_path in glob.glob(os.path.join(folder_path, '*.vfl')):
            base_name = Path(vex_file_path).stem
            vex_files.append((vex_file_path, base_name))

    return vex_files


def rename_vex_file(file_path: str, new_name: str) -> tuple[str, str]:
    if not new_name.endswith('.vfl'):
        new_name = f'{new_name}.vfl'

    if not utils.is_valid_file_name(new_name):
        new_file_path = file_path

        logger.error(f'{new_name!r} is not a valid file name.')
    elif not os.path.exists(file_path):
        new_file_path = file_path

        logger.error(f'{file_path!r} does not exit.')
    elif not os.path.isfile(file_path):
        new_file_path = file_path

        logger.error(f'{file_path!r} is a directory.')
    else:
        folder_path = os.path.dirname(file_path)

        for file in glob.glob(os.path.join(folder_path, '*')):
            if new_name == Path(file).stem:
                logger.error(f'{file_path!r} already exists.')

        new_file_path = os.path.join(folder_path, new_name)

        if os.path.normpath(new_file_path) == os.path.normpath(file_path):
            new_file_path = file_path

            logger.debug(f'{new_file_path!r} is the same name.')
        elif os.path.exists(new_file_path):
            new_file_path = file_path

            logger.error(f'{new_file_path!r} already exists.')
        else:
            os.rename(file_path, new_file_path)

            logger.debug(f'Renamed file {file_path!r} -> {new_file_path!r}')

    base_name = Path(new_file_path).stem

    return new_file_path, base_name
