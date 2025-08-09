"""消逝主题数值实体."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_INTEGRATION_TYPE,
    CONF_LOCATION_SOURCE_ID,
    INTEGRATION_TYPE_PAD,
    INTEGRATION_TYPE_PHONE,
    NUMBER_THEME_PAD_HUE,
    NUMBER_THEME_PHONE_MODE_PREFIX,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the 消逝主题 numbers."""
    integration_type = config_entry.data.get(CONF_INTEGRATION_TYPE)
    location_source_id = config_entry.data.get(CONF_LOCATION_SOURCE_ID)
    
    entities = []
    
    if integration_type == INTEGRATION_TYPE_PAD:
        # 平板主题数值
        entities.append(XiaoshiThemePadHueNumber(hass, config_entry))
    elif integration_type == INTEGRATION_TYPE_PHONE:
        # 获取设备名称
        entity = hass.states.get(location_source_id)
        device_name = ""
        if entity and entity.attributes.get("friendly_name"):
            device_name = entity.attributes.get("friendly_name")
        
        # 手机主题数值
        entities.append(XiaoshiThemePhoneModeNumber(hass, config_entry, device_name))
    
    async_add_entities(entities)


class XiaoshiThemePadHueNumber(NumberEntity):
    """平板端色相数值."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_native_min_value = 1
    _attr_native_max_value = 360
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """初始化平板端色相数值."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_pad_hue_number"
        self._attr_name = "平板端色相"
        self._attr_native_value = 1
        self.entity_id = NUMBER_THEME_PAD_HUE

    async def async_set_native_value(self, value: float) -> None:
        """设置数值."""
        self._attr_native_value = int(value)
        self.async_write_ha_state()


class XiaoshiThemePhoneModeNumber(NumberEntity):
    """手机端模式数值."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_native_min_value = 1
    _attr_native_max_value = 8
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, device_name: str) -> None:
        """初始化手机端模式数值."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_phone_mode_number"
        self._attr_name = f"手机端模式-{device_name}"
        self._attr_native_value = 1
        
        # 获取已有的手机主题数量，用于生成实体ID
        count = self._get_phone_theme_count()
        self.entity_id = f"{NUMBER_THEME_PHONE_MODE_PREFIX}{count}"
    
    def _get_phone_theme_count(self) -> int:
        """获取已有的手机主题数量."""
        count = 1
        while self.hass.states.get(f"{NUMBER_THEME_PHONE_MODE_PREFIX}{count}"):
            count += 1
        return count

    async def async_set_native_value(self, value: float) -> None:
        """设置数值."""
        self._attr_native_value = int(value)
        self.async_write_ha_state()