from __future__ import annotations

import hou

import logging
import os

from vex_manager.config import WrangleNodes


logger = logging.getLogger(f'vex_manager.{__name__}')


def get_current_parent_node() -> hou.Node | None:
    pane_tabs = hou.ui.paneTabs()

    for pane_tab in pane_tabs:
        if isinstance(pane_tab, hou.NetworkEditor):
            if pane_tab.isCurrentTab():
                parent_node = pane_tab.pwd()

                return parent_node


def create_wrangle_node(wrangle_type: str) -> hou.Node | None:
    wrangle_node = None
    selected_nodes = hou.selectedNodes()

    if selected_nodes:
        selected_node = selected_nodes[0]

        if not selected_node.outputNames():
            logger.error(f'{selected_node.name()!r} has no outputs.')
            return

        wrangle_node = selected_node.createOutputNode(wrangle_type)
        wrangle_node.setSelected(True)
    else:
        parent_node = get_current_parent_node()

        if parent_node:
            try:
                wrangle_node = parent_node.createNode(wrangle_type)
                wrangle_node.setSelected(True)
            except hou.OperationFailed:
                logger.error(f'Invalid context to create {wrangle_type!r} node.')
        else:
            logger.error(f'Could not create wrangle node {wrangle_type!r}. Parent not found.')

    return wrangle_node


def insert_vex_code(node: hou.Node, vex_file_path: str) -> None:
    if not vex_file_path:
        logger.warning('There is no VEX preset selected to insert.')
    elif not os.path.exists(vex_file_path):
        logger.error(f'{vex_file_path!r} does not exists.')
    else:
        with open(vex_file_path) as file_for_read:
            code = file_for_read.read()

        wrangle_node_types = [node.value[1] for node in WrangleNodes]

        if node.type().name() in wrangle_node_types:
            snippet_parm = node.parm('snippet')
            current_code = snippet_parm.evalAsString()

            if current_code:
                new_code = f'{current_code}\n\n{code}'
            else:
                new_code = code

            snippet_parm.set(new_code)
        else:
            logger.error(f'{node.name()!r} is not a wrangle node.')
