import logging


logging.basicConfig(format=f'%(levelname)s: [VEX Manager] %(message)s')
logger = logging.getLogger('vex_manager')
logger.setLevel(logging.DEBUG)
