"""消逝主题集成."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, UPDATE_INTERVAL_MINUTES, HUE_UPDATE_INTERVAL_MINUTES
from .coordinator import async_setup_coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SWITCH, Platform.SELECT, Platform.NUMBER]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the 消逝主题 component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up 消逝主题 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # 如果是第一个条目，设置协调器
    if len([k for k in hass.data[DOMAIN].keys() if k not in ["update_remove", "hue_update_remove"]]) == 1:
        _LOGGER.info("设置消逝主题协调器")
        await async_setup_coordinator(hass)
    else:
        _LOGGER.info("已存在消逝主题协调器，跳过设置")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # 如果是最后一个条目，清理定时任务
        remaining_entries = [k for k in hass.data[DOMAIN].keys() 
                            if k not in ["update_remove", "hue_update_remove", "update_callback"]]
        
        if not remaining_entries:
            _LOGGER.info("移除所有消逝主题条目，清理定时任务")
            
            if "update_remove" in hass.data[DOMAIN]:
                _LOGGER.info("移除主题更新定时任务")
                hass.data[DOMAIN]["update_remove"]()
                hass.data[DOMAIN].pop("update_remove")
            
            if "hue_update_remove" in hass.data[DOMAIN]:
                _LOGGER.info("移除色相更新定时任务")
                hass.data[DOMAIN]["hue_update_remove"]()
                hass.data[DOMAIN].pop("hue_update_remove")
                
            _LOGGER.info("消逝主题定时任务已清理")

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """重新加载配置条目."""
    _LOGGER.info("重新加载消逝主题集成")
    
    # 先卸载
    await async_unload_entry(hass, entry)
    
    # 再重新加载
    await async_setup_entry(hass, entry)
    
    _LOGGER.info("消逝主题集成重新加载完成")