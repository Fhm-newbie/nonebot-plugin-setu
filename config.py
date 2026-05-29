from pydantic import BaseModel
from nonebot import get_driver


class Config(BaseModel):
    # Your Config Here
    proxies: str = None
    transpose: bool = False


#setu_config = Config.parse_obj(get_driver().config)
setu_config = Config.model_validate(get_driver().config.model_dump())
