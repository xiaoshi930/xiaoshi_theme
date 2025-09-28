"""消逝主题选择器实体."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    CONF_INTEGRATION_TYPE,
    INTEGRATION_TYPE_PAD,
    SELECT_THEME_PAD_MODE,
    PAD_MODE_OPTIONS,
    PAD_MODE_COLOR,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the 消逝主题 selects."""
    integration_type = config_entry.data.get(CONF_INTEGRATION_TYPE)
    
    entities = []
    
    if integration_type == INTEGRATION_TYPE_PAD:
        # 平板主题选择器
        entities.append(XiaoshiThemePadModeSelect(hass, config_entry))
    
    async_add_entities(entities)


class XiaoshiThemePadModeSelect(SelectEntity, RestoreEntity):
    """平板端模式选择器."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """初始化平板端模式选择器."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_pad_mode_select"
        self._attr_name = "平板端模式"
        self._attr_options = PAD_MODE_OPTIONS
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"xiaoshi_theme_{config_entry.entry_id}")},
            name="消逝主题-平板",
            manufacturer="Xiaoshi Theme Integration",
            model="Xiaoshi Theme Select",
        )
        self._attr_current_option = PAD_MODE_COLOR
        self.entity_id = SELECT_THEME_PAD_MODE
        
    async def async_added_to_hass(self) -> None:
        """当实体被添加到 HA 时调用."""
        await super().async_added_to_hass()
        
        # 尝试恢复之前的状态
        last_state = await self.async_get_last_state()
        if last_state and last_state.state in PAD_MODE_OPTIONS:
            self._attr_current_option = last_state.state
            _LOGGER.debug(f"恢复 {self.entity_id} 的状态为: {self._attr_current_option}")

    async def async_select_option(self, option: str) -> None:
        """更改选项."""
        self._attr_current_option = option
        self.async_write_ha_state()
