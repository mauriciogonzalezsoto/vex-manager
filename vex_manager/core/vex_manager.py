import hou

import logging

from vex_manager.config import WrangleNodes


logger = logging.getLogger(f"vex_manager.{__name__}")


def set_vex_code_in_selected_wrangle_node(vex_code: str, insert: bool = False) -> None:
    if vex_code:
        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            node = selected_nodes[-1]
            wrangle_node_types = [node.value for node in WrangleNodes]

            if node.type().name() in wrangle_node_types:
                parms = [parm.name() for parm in node.parms()]

                if "snippet" in parms:
                    snippet_parm = node.parm("snippet")
                elif "vexsnippet" in parms:
                    snippet_parm = node.parm("vexsnippet")
                else:
                    logger.error("No snippet parm found.")

                    return

                if insert:
                    current_code = snippet_parm.evalAsString()

                    if current_code:
                        new_vex_code = f"{current_code}\n\n{vex_code}"
                    else:
                        new_vex_code = vex_code
                else:
                    new_vex_code = vex_code

                snippet_parm.set(new_vex_code)
            else:
                logger.error(f"{node.name()!r} is not a wrangle node.")
        else:
            logger.error("There is no selected node.")
