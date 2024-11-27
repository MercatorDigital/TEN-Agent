#
#
# Agora Real Time Engagement
# Created by Tomas Liu in 2024-08.
# Copyright (c) 2024 Agora IO. All rights reserved.
#
#
from ten import (
    Addon,
    register_addon_as_extension,
    TenEnv,
)


@register_addon_as_extension("dnd_spells_tool_python")
class DndAddon(Addon):

    def on_create_instance(self, ten_env: TenEnv, name: str, context) -> None:
        from .extension import DndExtension
        from .log import logger
        logger.info("DND on_create_instance")
        ten_env.on_create_instance_done(DndExtension(name), context)
