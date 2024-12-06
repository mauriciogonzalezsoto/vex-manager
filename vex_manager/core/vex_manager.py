from __future__ import annotations

import hou

import logging
import os


logger = logging.getLogger(f'vex_manager.{__name__}')


def get_current_parent_node() -> hou.Node | None:
    pane_tabs = hou.ui.paneTabs()

    for pane_tab in pane_tabs:
        if isinstance(pane_tab, hou.NetworkEditor):
            if pane_tab.isCurrentTab():
                parent_node = pane_tab.pwd()

                return parent_node


def create_wrangle_node(wrangle_type: str) -> hou.Node | None:
    selected_nodes = hou.selectedNodes()

    if selected_nodes:
        parent_node = selected_nodes[0]
    else:
        parent_node = get_current_parent_node()

    if parent_node:
        try:
            wrangle_node = parent_node.createNode(wrangle_type)
            wrangle_node.setSelected(True)

            return wrangle_node
        except hou.OperationFailed:
            logger.error(f'Invalid context to create \'{wrangle_type}\' node.')
    else:
        logger.error(f'Could not create wrangle node \'{wrangle_type}\'. Parent not found.')


def insert_vex_code(node: hou.Node, vex_file_path: str) -> None:
    if os.path.exists(vex_file_path):
        with open(vex_file_path) as file_for_read:
            code = file_for_read.read()

        node_parm_names = [parm.name() for parm in node.parms()]

        if 'snippet' in node_parm_names:
            snippet_parm = node.parm('snippet')
            current_code = snippet_parm.evalAsString()

            if current_code:
                new_code = f'{current_code}\n\n{code}'
            else:
                new_code = code

            snippet_parm.set(new_code)
        else:
            logger.error(f'Can not insert VEX code in the selected node \'{node.name()}\'.')
    else:
        logger.error(f'\'{vex_file_path}\' does not exists.')
