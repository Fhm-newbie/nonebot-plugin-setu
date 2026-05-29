import json
import re
from pathlib import Path

from nonebot import get_driver
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from nonebot.typing import T_State

from .model import GetSetuConfig
from .model import GroupConfig
from .setu import Setu

driver = get_driver()

global_config = driver.config
digitalConversionDict = {
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}
callsetu = on_regex('来(.*?)[点丶、个份张幅](.*?)的?([rR]18)?[色瑟涩䔼😍🐍][图圖🤮]', priority=5)


@callsetu.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    config_getSetu: GetSetuConfig = GetSetuConfig()
    info = state["_matched"]
    pattern = r"来(.*?)[点丶、个份张幅](.*?)的?([rR]18)?[色瑟涩䔼][图圖]"
    res = re.findall(pattern, info[0])[0]  # 来一张r18色图 -> ['一', '', 'r18']
    logger.debug(f"res: {res}")
    if res[0] != "":
        if res[0] in digitalConversionDict.keys():
            config_getSetu.toGetNum = int(digitalConversionDict[res[0]])
        else:
            if res[0].isdigit():
                config_getSetu.toGetNum = int(res[0])
            else:
                await callsetu.send(MessageSegment.text("请使用阿拉伯数字"))
                logger.warnning("非数字")
                return None
    else:  # 未指定数量,默认1
        config_getSetu.toGetNum = 1
    config_getSetu.tags = [i for i in set(re.split(r"[,， ]", res[1])) if i != ""]
    if res[2]:  # r18关键字
        config_getSetu.level = 1
    await Setu(event, bot, config_getSetu).main()


@driver.on_bot_connect
async def buildConfig(bot: Bot):
    curFileDir = Path(__file__).absolute().parent  # 当前文件路径
    logger.info("开始更新所有群数据~")
    for group in await bot.get_group_list():
        groupid = group["group_id"]
        filePath = (
                curFileDir
                / "database"
                / "DB"
                / "configs"
                / "{}.json".format(groupid)
        )
        if filePath.is_file():
            logger.info("群:{} 配置文件已存在".format(groupid))
            continue
        with open(filePath, "w", encoding="utf-8") as f:
            json.dump(
                GroupConfig().dict(), f, indent=4, ensure_ascii=False
            )
        logger.success("%s.json创建成功" % groupid)
    logger.success("更新群信息成功~")
