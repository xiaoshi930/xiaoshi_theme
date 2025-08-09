"""Config flow for 消逝主题 integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_INTEGRATION_TYPE,
    INTEGRATION_TYPE_PAD,
    INTEGRATION_TYPE_PHONE,
    CONF_LOCATION_SOURCE,
    CONF_LOCATION_SOURCE_ID,
)

_LOGGER = logging.getLogger(__name__)

async def _async_has_pad_theme(hass: HomeAssistant) -> bool:
    """检查是否已经添加了平板主题."""
    existing_entries = hass.config_entries.async_entries(DOMAIN)
    for entry in existing_entries:
        if entry.data.get(CONF_INTEGRATION_TYPE) == INTEGRATION_TYPE_PAD:
            return True
    return False

class XiaoshiThemeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 消逝主题."""

    VERSION = 1
    
    def __init__(self):
        """Initialize the config flow."""
        self._integration_type = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        # 检查是否已经添加了平板主题
        has_pad_theme = await _async_has_pad_theme(self.hass)

        # 如果已经添加了平板主题，只显示手机主题选项
        if has_pad_theme:
            return await self.async_step_integration_type({CONF_INTEGRATION_TYPE: INTEGRATION_TYPE_PHONE})

        # 否则显示选择集成类型的选项
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_INTEGRATION_TYPE): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=[
                                    {"label": "平板主题", "value": INTEGRATION_TYPE_PAD},
                                    {"label": "手机主题", "value": INTEGRATION_TYPE_PHONE},
                                ],
                                mode=selector.SelectSelectorMode.DROPDOWN,
                            )
                        ),
                    }
                ),
            )

        return await self.async_step_integration_type(user_input)

    async def async_step_integration_type(self, user_input=None) -> FlowResult:
        """处理集成类型选择."""
        if user_input is None:
            return self.async_abort(reason="invalid_input")
            
        integration_type = user_input[CONF_INTEGRATION_TYPE]
        self._integration_type = integration_type

        # 如果选择了平板主题，但已经添加过，则显示错误
        if integration_type == INTEGRATION_TYPE_PAD:
            has_pad_theme = await _async_has_pad_theme(self.hass)
            if has_pad_theme:
                return self.async_abort(reason="pad_theme_already_exists")

        # 进入位置源选择步骤
        return await self.async_step_location_source()

    async def async_step_location_source(self, user_input=None) -> FlowResult:
        """处理位置源选择."""
        errors = {}
        integration_type = self._integration_type
        
        if integration_type is None:
            return self.async_abort(reason="invalid_input")

        if user_input is not None and CONF_LOCATION_SOURCE_ID in user_input:
            location_source_id = user_input[CONF_LOCATION_SOURCE_ID]

            # 创建配置条目
            title = "消逝主题 - 平板" if integration_type == INTEGRATION_TYPE_PAD else f"消逝主题 - 手机"
            
            # 如果是手机主题，添加设备名称到标题
            if integration_type == INTEGRATION_TYPE_PHONE and location_source_id:
                entity = self.hass.states.get(location_source_id)
                if entity and entity.attributes.get("friendly_name"):
                    title = f"消逝主题 - 手机 - {entity.attributes.get('friendly_name')}"
            
            return self.async_create_entry(
                title=title,
                data={
                    CONF_INTEGRATION_TYPE: integration_type,
                    CONF_LOCATION_SOURCE_ID: location_source_id,
                },
            )

        # 构建位置源选择表单
        source_types = ["zone", "device_tracker"]
        source_options = []
        
        for source_type in source_types:
            entities = self.hass.states.async_entity_ids(source_type)
            for entity_id in entities:
                entity = self.hass.states.get(entity_id)
                if entity:
                    friendly_name = entity.attributes.get("friendly_name", entity_id)
                    source_options.append(
                        {"label": f"{friendly_name} ({entity_id})", "value": entity_id}
                    )

        if not source_options:
            return self.async_abort(reason="no_location_sources")

        return self.async_show_form(
            step_id="location_source",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOCATION_SOURCE_ID): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=source_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "integration_type": "平板主题" if self._integration_type == INTEGRATION_TYPE_PAD else "手机主题"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)