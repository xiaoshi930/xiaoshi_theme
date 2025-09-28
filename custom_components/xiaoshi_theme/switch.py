"""消逝主题开关实体."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    CONF_INTEGRATION_TYPE,
    CONF_LOCATION_SOURCE_ID,
    INTEGRATION_TYPE_PAD,
    INTEGRATION_TYPE_PHONE,
    SWITCH_THEME_PAD_FULL,
    SWITCH_THEME_PAD_MODE,
    SWITCH_THEME_PAD_HUE,
    SWITCH_THEME_PHONE_FULL_PREFIX,
    SWITCH_THEME_PHONE_MODE_PREFIX,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the 消逝主题 switches."""
    integration_type = config_entry.data.get(CONF_INTEGRATION_TYPE)
    location_source_id = config_entry.data.get(CONF_LOCATION_SOURCE_ID)
    
    entities = []
    
    if integration_type == INTEGRATION_TYPE_PAD:
        # 平板主题开关
        entities.extend([
            XiaoshiThemePadFullSwitch(hass, config_entry),
            XiaoshiThemePadModeSwitch(hass, config_entry),
            XiaoshiThemePadHueSwitch(hass, config_entry),
        ])
    elif integration_type == INTEGRATION_TYPE_PHONE:
        # 获取设备名称
        entity = hass.states.get(location_source_id)
        device_name = ""
        if entity and entity.attributes.get("friendly_name"):
            device_name = entity.attributes.get("friendly_name")
        
        # 手机主题开关
        entities.extend([
            XiaoshiThemePhoneFullSwitch(hass, config_entry, device_name),
            XiaoshiThemePhoneModeSwitch(hass, config_entry, device_name),
        ])
    
    async_add_entities(entities)


class XiaoshiThemeBaseSwitch(SwitchEntity, RestoreEntity):
    """消逝主题基础开关类."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """初始化基础开关."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_is_on = True
        
    async def async_added_to_hass(self) -> None:
        """当实体被添加到 HA 时调用."""
        await super().async_added_to_hass()
        
        # 尝试恢复之前的状态
        last_state = await self.async_get_last_state()
        if last_state:
            self._attr_is_on = last_state.state == "on"
            _LOGGER.debug(f"恢复 {self.entity_id} 的状态为: {self._attr_is_on}")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """打开开关."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """关闭开关."""
        self._attr_is_on = False
        self.async_write_ha_state()


class XiaoshiThemePadFullSwitch(XiaoshiThemeBaseSwitch):
    """平板端全屏切换开关."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """初始化平板端全屏切换开关."""
        super().__init__(hass, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_pad_full"
        self._attr_name = "平板端全屏切换"
        self.entity_id = SWITCH_THEME_PAD_FULL
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"xiaoshi_theme_{config_entry.entry_id}")},
            name="消逝主题-平板",
            manufacturer="Xiaoshi Theme Integration",
            model="Xiaoshi Theme Switch",
        )


class XiaoshiThemePadModeSwitch(XiaoshiThemeBaseSwitch):
    """平板端模式启用开关."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """初始化平板端模式启用开关."""
        super().__init__(hass, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_pad_mode"
        self._attr_name = "平板端模式启用"
        self.entity_id = SWITCH_THEME_PAD_MODE
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"xiaoshi_theme_{config_entry.entry_id}")},
            name="消逝主题-平板",
            manufacturer="Xiaoshi Theme Integration",
            model="Xiaoshi Theme Switch",
        )


class XiaoshiThemePadHueSwitch(XiaoshiThemeBaseSwitch):
    """平板端色相启用开关."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """初始化平板端色相启用开关."""
        super().__init__(hass, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_pad_hue"
        self._attr_name = "平板端色相启用"
        self.entity_id = SWITCH_THEME_PAD_HUE
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"xiaoshi_theme_{config_entry.entry_id}")},
            name="消逝主题-平板",
            manufacturer="Xiaoshi Theme Integration",
            model="Xiaoshi Theme Switch",
        )


class XiaoshiThemePhoneFullSwitch(XiaoshiThemeBaseSwitch):
    """手机端全屏切换开关."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, device_name: str) -> None:
        """初始化手机端全屏切换开关."""
        super().__init__(hass, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_phone_full"
        self._attr_name = f"手机端全屏切换-{device_name}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"xiaoshi_theme_{config_entry.entry_id}")},
            name="消逝主题-手机",
            manufacturer="Xiaoshi Theme Integration",
            model="Xiaoshi Theme Number",
        )
        
        # 获取已有的手机主题数量，用于生成实体ID
        count = self._get_phone_theme_count()
        self.entity_id = f"{SWITCH_THEME_PHONE_FULL_PREFIX}{count}"
    
    def _get_phone_theme_count(self) -> int:
        """获取已有的手机主题数量."""
        count = 1
        while self.hass.states.get(f"{SWITCH_THEME_PHONE_FULL_PREFIX}{count}"):
            count += 1
        return count


class XiaoshiThemePhoneModeSwitch(XiaoshiThemeBaseSwitch):
    """手机端模式启用开关."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, device_name: str) -> None:
        """初始化手机端模式启用开关."""
        super().__init__(hass, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_phone_mode"
        self._attr_name = f"手机端模式启用-{device_name}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"xiaoshi_theme_{config_entry.entry_id}")},
            name="消逝主题-手机",
            manufacturer="Xiaoshi Theme Integration",
            model="Xiaoshi Theme Number",
        )
        
        # 获取已有的手机主题数量，用于生成实体ID
        count = self._get_phone_theme_count()
        self.entity_id = f"{SWITCH_THEME_PHONE_MODE_PREFIX}{count}"
    
    def _get_phone_theme_count(self) -> int:
        """获取已有的手机主题数量."""
        count = 1
        while self.hass.states.get(f"{SWITCH_THEME_PHONE_MODE_PREFIX}{count}"):
            count += 1
        return count
