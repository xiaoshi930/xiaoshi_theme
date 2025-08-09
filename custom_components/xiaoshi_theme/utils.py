"""消逝主题工具函数."""
import logging
from datetime import datetime
from typing import Optional, Tuple

from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
)
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
import astral
from astral.sun import sun

_LOGGER = logging.getLogger(__name__)

def is_daytime(hass: HomeAssistant, latitude: float, longitude: float) -> bool:
    """根据经纬度判断是白天还是黑夜."""
    try:
        # 获取当前时间
        now = dt_util.now()
        
        # 使用astral库计算日出日落时间
        observer = astral.Observer(latitude=latitude, longitude=longitude)
        s = sun(observer, date=now.date())
        
        # 判断当前时间是否在日出和日落之间
        return s["sunrise"] <= now <= s["sunset"]
    except Exception as e:
        _LOGGER.error("计算日出日落时间出错: %s", e)
        # 出错时默认为白天
        return True

def get_location_from_entity(hass: HomeAssistant, entity_id: str) -> Tuple[Optional[float], Optional[float]]:
    """从实体获取位置信息."""
    entity = hass.states.get(entity_id)
    if not entity:
        _LOGGER.error("实体 %s 不存在", entity_id)
        return None, None
    
    # 尝试从实体属性中获取经纬度
    latitude = entity.attributes.get(ATTR_LATITUDE)
    longitude = entity.attributes.get(ATTR_LONGITUDE)
    
    if latitude is None or longitude is None:
        _LOGGER.error("实体 %s 没有位置信息", entity_id)
        return None, None
    
    return latitude, longitude