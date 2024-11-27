import json
import requests

from typing import Any, List

from ten import (
    AudioFrame,
    VideoFrame,
    Extension,
    TenEnv,
    Cmd,
    StatusCode,
    CmdResult,
    Data,
)
from .log import logger

CMD_TOOL_REGISTER = "tool_register"
CMD_TOOL_CALL = "tool_call"
CMD_PROPERTY_NAME = "name"
CMD_PROPERTY_ARGS = "args"

TOOL_REGISTER_PROPERTY_NAME = "name"
TOOL_REGISTER_PROPERTY_DESCRIPTON = "description"
TOOL_REGISTER_PROPERTY_PARAMETERS = "parameters"
TOOL_CALLBACK = "callback"

TOOL_NAME = "run_example"
TOOL_DESCRIPTION = "When the user mentions DND, use this tool to get the name of the spell specified by the user."
TOOL_PARAMETERS = {
        "type": "object",
        "properties": {
            "filling": {
                "type": "string",
                "description": "the spell name specified by the user"
            }
        },
        "required": ["filling"],
    }

TOOL_NAME2 = "run_example2"
TOOL_DESCRIPTION2 = "When the user mentions DND, use this tool to get the name of the class specified by the user."
TOOL_PARAMETERS2 = {
        "type": "object",
        "properties": {
            "filling": {
                "type": "string",
                "description": "the class specified by the user"
            }
        },
        "required": ["filling"],
    }


class EXAMPLEToolExtension(Extension):
    tools: dict = {}
    k: int = 10
    ten_env: Any = None
    api_key: str = ""

    def on_init(self, ten_env: TenEnv) -> None:
        logger.info("EXAMPLEToolExtension on_init")
        self.ten_env = ten_env
        self.tools = {
            TOOL_NAME: {
                TOOL_REGISTER_PROPERTY_NAME: TOOL_NAME,
                TOOL_REGISTER_PROPERTY_DESCRIPTON: TOOL_DESCRIPTION,
                TOOL_REGISTER_PROPERTY_PARAMETERS: TOOL_PARAMETERS,
                TOOL_CALLBACK: self._run_example
            },
            TOOL_NAME2: {
                TOOL_REGISTER_PROPERTY_NAME: TOOL_NAME2,
                TOOL_REGISTER_PROPERTY_DESCRIPTON: TOOL_DESCRIPTION2,
                TOOL_REGISTER_PROPERTY_PARAMETERS: TOOL_PARAMETERS2,
                TOOL_CALLBACK: self._run_example2
            }
        }

        ten_env.on_init_done()

    def on_start(self, ten_env: TenEnv) -> None:
        logger.info("EXAMPLEToolExtension on_start")
        self.api_key = ten_env.get_property_string("api_key")
        
        # Register func
        for name, tool in self.tools.items():
            c = Cmd.create(CMD_TOOL_REGISTER)
            c.set_property_string(TOOL_REGISTER_PROPERTY_NAME, name)
            c.set_property_string(TOOL_REGISTER_PROPERTY_DESCRIPTON, tool[TOOL_REGISTER_PROPERTY_DESCRIPTON])
            c.set_property_string(TOOL_REGISTER_PROPERTY_PARAMETERS, json.dumps(tool[TOOL_REGISTER_PROPERTY_PARAMETERS]))
            ten_env.send_cmd(c, lambda ten, result: logger.info(f"register done, {result}"))

        ten_env.on_start_done()

    def on_stop(self, ten_env: TenEnv) -> None:
        logger.info("EXAMPLEToolExtension on_stop")
        ten_env.on_stop_done()

    def on_deinit(self, ten_env: TenEnv) -> None:
        logger.info("EXAMPLEToolExtension on_deinit")
        ten_env.on_deinit_done()

    def on_cmd(self, ten_env: TenEnv, cmd: Cmd) -> None:
        cmd_name = cmd.get_name()
        logger.info(f"on_cmd name {cmd_name} {cmd.to_json()}")

        # FIXME need to handle async
        try:
            name = cmd.get_property_string(CMD_PROPERTY_NAME)
            if name in self.tools:
                try:
                    tool = self.tools[name]
                    args = cmd.get_property_string(CMD_PROPERTY_ARGS)
                    arg_dict = json.loads(args)
                    logger.info(f"before callback {name}")
                    resp = tool[TOOL_CALLBACK](arg_dict)
                    logger.info(f"after callback {resp}")
                    cmd_result = CmdResult.create(StatusCode.OK)
                    cmd_result.set_property_string("response", json.dumps(resp))
                    ten_env.return_result(cmd_result, cmd)
                    return
                except:
                    logger.exception("Failed to callback")
                    cmd_result = CmdResult.create(StatusCode.ERROR)
                    ten_env.return_result(cmd_result, cmd)
                    return
            else:
                logger.error(f"unknown tool name {name}")
        except:
            logger.exception("Failed to get tool name")
            cmd_result = CmdResult.create(StatusCode.ERROR)
            ten_env.return_result(cmd_result, cmd)
            return
            
        cmd_result = CmdResult.create(StatusCode.OK)
        ten_env.return_result(cmd_result, cmd)

    def on_data(self, ten_env: TenEnv, data: Data) -> None:
        pass

    def on_audio_frame(self, ten_env: TenEnv, audio_frame: AudioFrame) -> None:
        pass

    def on_video_frame(self, ten_env: TenEnv, video_frame: VideoFrame) -> None:
        pass
    
    def _run_example(self,  args:dict) -> Any:
        logger.info("USING DND THING")
        if "filling" not in args:
            raise Exception("Failed to get property")
        
        spell: str = args["filling"]
        logger.info(f"EEEEEEEEEEEEEE https://www.dnd5eapi.co/api/spells/{spell.lower()}")
        url = f"https://www.dnd5eapi.co/api/spells/{spell.lower()}"
        response = requests.get(url)

        logger.info(f"FFFFFF {response}")

        result = response.json()
        return result

        
    def _run_example2(self,  args:dict) -> Any:
        logger.info("USING DND THING 2")
        if "filling" not in args:
            raise Exception("Failed to get property")
        
        spell: str = args["filling"]
        logger.info(f"ZZZZZZZZ https://www.dnd5eapi.co/api/classes/{spell.lower()}")
        url = f"https://www.dnd5eapi.co/api/classes/{spell.lower()}"
        response = requests.get(url)

        logger.info(f"XXXXXXXX {response}")

        result = response.json()
        return result
        

        
