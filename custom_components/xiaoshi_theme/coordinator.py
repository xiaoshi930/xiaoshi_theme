"""消逝主题定时任务协调器."""
import logging
import datetime
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_INTEGRATION_TYPE,
    CONF_LOCATION_SOURCE_ID,
    INTEGRATION_TYPE_PAD,
    INTEGRATION_TYPE_PHONE,
    SWITCH_THEME_PAD_MODE,
    SELECT_THEME_PAD_MODE,
    SWITCH_THEME_PAD_HUE,
    NUMBER_THEME_PAD_HUE,
    SWITCH_THEME_PHONE_MODE_PREFIX,
    NUMBER_THEME_PHONE_MODE_PREFIX,
    PAD_MODE_COLOR,
    PAD_MODE_BLACK,
    UPDATE_INTERVAL_MINUTES,
    HUE_UPDATE_INTERVAL_MINUTES,
)
from .utils import is_daytime, get_location_from_entity

_LOGGER = logging.getLogger(__name__)

async def async_setup_coordinator(hass: HomeAssistant) -> None:
    """设置定时任务协调器."""
    
    async def update_theme_logic(now=None) -> None:
        """更新主题逻辑."""
        try:
            if now:
                _LOGGER.debug("开始执行主题更新逻辑，时间：%s", now)
            else:
                _LOGGER.debug("开始执行主题更新逻辑，时间未提供")
                
            # 处理平板主题逻辑
            await update_pad_theme_logic(hass)
            
            # 处理手机主题逻辑
            await update_phone_theme_logic(hass)
            
            _LOGGER.debug("主题更新定时任务执行完成，时间：%s", now)
        except Exception as e:
            _LOGGER.error("主题更新定时任务执行出错: %s", e)
    
    # 注册色相更新定时任务 - 每1分钟执行一次
    async def update_hue_logic(now=None) -> None:
        """更新色相逻辑."""
        try:
            if now:
                _LOGGER.debug("开始执行色相更新逻辑，时间：%s", now)
            else:
                _LOGGER.debug("开始执行色相更新逻辑，时间未提供")
                
            # 获取平板主题实体
            pad_hue_switch = hass.states.get(SWITCH_THEME_PAD_HUE)
            pad_hue_number = hass.states.get(NUMBER_THEME_PAD_HUE)
            
            if not all([pad_hue_switch, pad_hue_number]):
                _LOGGER.warning("平板主题色相实体不完整")
                return
                
            _LOGGER.debug("平板主题色相开关状态: %s, 当前色相: %s", 
                         pad_hue_switch.state, pad_hue_number.state)
                
            # 处理逻辑3和逻辑4：色相自动变化
            if pad_hue_switch.state == "on":
                current_hue = int(float(pad_hue_number.state))
                new_hue = current_hue + 1
                if new_hue > 360:
                    new_hue = 1
                
                _LOGGER.debug("更新平板主题色相: %s -> %s", current_hue, new_hue)
                
                await hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": NUMBER_THEME_PAD_HUE, "value": new_hue},
                )
                _LOGGER.debug("平板主题色相已更新为 %s，时间：%s", new_hue, now)
            else:
                _LOGGER.debug("平板主题色相开关已关闭，不执行更新")
            
            _LOGGER.debug("色相更新定时任务执行完成，时间：%s", now)
        except Exception as e:
            _LOGGER.error("色相更新定时任务执行出错: %s", e)
    
    # 使用 async_track_time_interval 注册定时任务
    _LOGGER.info("正在注册主题更新定时任务，间隔：%s 分钟", UPDATE_INTERVAL_MINUTES)
    update_interval = timedelta(minutes=UPDATE_INTERVAL_MINUTES)
    
    # 包装回调函数，确保时间参数正确传递
    async def theme_callback(now):
        _LOGGER.debug("主题更新定时任务被触发，时间：%s", now)
        await update_theme_logic(now)
    
    hass.data[DOMAIN]["update_remove"] = async_track_time_interval(
        hass, theme_callback, update_interval
    )
    
    _LOGGER.info("正在注册色相更新定时任务，间隔：%s 分钟", HUE_UPDATE_INTERVAL_MINUTES)
    hue_update_interval = timedelta(minutes=HUE_UPDATE_INTERVAL_MINUTES)
    
    # 包装回调函数，确保时间参数正确传递
    async def hue_callback(now):
        _LOGGER.debug("色相更新定时任务被触发，时间：%s", now)
        await update_hue_logic(now)
    
    hass.data[DOMAIN]["hue_update_remove"] = async_track_time_interval(
        hass, hue_callback, hue_update_interval
    )
    
    # 初始执行一次
    _LOGGER.info("初始执行主题更新和色相更新")
    now = datetime.datetime.now()
    _LOGGER.debug("初始执行时间：%s", now)
    await update_theme_logic(now)
    await update_hue_logic(now)


async def update_pad_theme_logic(hass: HomeAssistant) -> None:
    """更新平板主题逻辑."""
    try:
        _LOGGER.debug("开始执行平板主题更新逻辑")
        
        # 查找平板主题配置
        pad_entry = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get(CONF_INTEGRATION_TYPE) == INTEGRATION_TYPE_PAD:
                pad_entry = entry
                break
        
        if not pad_entry:
            _LOGGER.debug("未找到平板主题配置")
            return
        
        # 获取平板主题实体
        pad_mode_switch = hass.states.get(SWITCH_THEME_PAD_MODE)
        pad_mode_select = hass.states.get(SELECT_THEME_PAD_MODE)
        pad_hue_switch = hass.states.get(SWITCH_THEME_PAD_HUE)
        pad_hue_number = hass.states.get(NUMBER_THEME_PAD_HUE)
        
        if not all([pad_mode_switch, pad_mode_select, pad_hue_switch, pad_hue_number]):
            _LOGGER.error("平板主题实体不完整")
            return
        
        _LOGGER.debug("平板主题模式开关状态: %s, 当前模式: %s", 
                     pad_mode_switch.state, pad_mode_select.state)
        
        # 处理逻辑1和逻辑2：根据白天黑夜切换模式
        if pad_mode_switch.state == "on":
            location_source_id = pad_entry.data.get(CONF_LOCATION_SOURCE_ID)
            _LOGGER.debug("使用位置源: %s", location_source_id)
            
            latitude, longitude = get_location_from_entity(hass, location_source_id)
            
            if latitude is not None and longitude is not None:
                _LOGGER.debug("获取到位置: 纬度 %s, 经度 %s", latitude, longitude)
                is_day = is_daytime(hass, latitude, longitude)
                _LOGGER.debug("当前是%s", "白天" if is_day else "黑夜")
                
                # 设置模式
                if is_day and pad_mode_select.state != PAD_MODE_COLOR:
                    await hass.services.async_call(
                        "select", "select_option",
                        {"entity_id": SELECT_THEME_PAD_MODE, "option": PAD_MODE_COLOR},
                    )
                    _LOGGER.info("平板主题模式已切换为彩平图（白天模式）")
                elif not is_day and pad_mode_select.state != PAD_MODE_BLACK:
                    await hass.services.async_call(
                        "select", "select_option",
                        {"entity_id": SELECT_THEME_PAD_MODE, "option": PAD_MODE_BLACK},
                    )
                    _LOGGER.info("平板主题模式已切换为黑平图（黑夜模式）")
                else:
                    _LOGGER.debug("平板主题模式无需切换")
            else:
                _LOGGER.warning("无法获取位置信息")
        else:
            _LOGGER.debug("平板主题模式开关已关闭，不执行切换")
        
        _LOGGER.debug("平板主题更新逻辑执行完成")
    except Exception as e:
        _LOGGER.error("平板主题更新逻辑执行出错: %s", e)


async def update_phone_theme_logic(hass: HomeAssistant) -> None:
    """更新手机主题逻辑."""
    try:
        _LOGGER.debug("开始执行手机主题更新逻辑")
        
        # 查找所有手机主题配置
        phone_entries = []
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get(CONF_INTEGRATION_TYPE) == INTEGRATION_TYPE_PHONE:
                phone_entries.append(entry)
        
        if not phone_entries:
            _LOGGER.debug("未找到手机主题配置")
            return
        
        _LOGGER.debug("找到 %s 个手机主题配置", len(phone_entries))
        
        # 处理每个手机主题
        for i, entry in enumerate(phone_entries, 1):
            mode_switch_id = f"{SWITCH_THEME_PHONE_MODE_PREFIX}{i}"
            mode_number_id = f"{NUMBER_THEME_PHONE_MODE_PREFIX}{i}"
            
            _LOGGER.debug("处理手机主题 %s: 开关=%s, 数值=%s", 
                         i, mode_switch_id, mode_number_id)
            
            mode_switch = hass.states.get(mode_switch_id)
            mode_number = hass.states.get(mode_number_id)
            
            if not mode_switch or not mode_number:
                _LOGGER.error("手机主题实体不完整: %s", entry.entry_id)
                continue
                
            _LOGGER.debug("手机主题 %s 开关状态: %s, 当前模式: %s", 
                         i, mode_switch.state, mode_number.state)
        
            # 处理逻辑1、2和3：根据白天黑夜切换模式
            if mode_switch.state == "on":
                location_source_id = entry.data.get(CONF_LOCATION_SOURCE_ID)
                _LOGGER.debug("手机主题 %s 使用位置源: %s", i, location_source_id)
                
                latitude, longitude = get_location_from_entity(hass, location_source_id)
                
                if latitude is not None and longitude is not None:
                    _LOGGER.debug("手机主题 %s 获取到位置: 纬度 %s, 经度 %s", i, latitude, longitude)
                    is_day = is_daytime(hass, latitude, longitude)
                    _LOGGER.debug("手机主题 %s 当前是%s", i, "白天" if is_day else "黑夜")
                    
                    current_mode = int(float(mode_number.state))
                    _LOGGER.debug("手机主题 %s 当前模式: %s", i, current_mode)
                    
                    # 白天模式处理 - 逻辑1
                    if is_day:
                        # 白天时如果是偶数模式，转换为奇数模式
                        if current_mode == 2:
                            new_mode = 1
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（白天模式）", i, new_mode)
                        elif current_mode == 4:
                            new_mode = 3
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（白天模式）", i, new_mode)
                        elif current_mode == 6:
                            new_mode = 5
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（白天模式）", i, new_mode)
                        elif current_mode == 8:
                            new_mode = 7
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（白天模式）", i, new_mode)
                        else:
                            _LOGGER.debug("手机主题 %s 当前为奇数模式 %s，白天无需切换", i, current_mode)
                    # 黑夜模式处理 - 逻辑2
                    else:
                        # 黑夜时如果是奇数模式，转换为偶数模式
                        if current_mode == 1:
                            new_mode = 2
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（黑夜模式）", i, new_mode)
                        elif current_mode == 3:
                            new_mode = 4
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（黑夜模式）", i, new_mode)
                        elif current_mode == 5:
                            new_mode = 6
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（黑夜模式）", i, new_mode)
                        elif current_mode == 7:
                            new_mode = 8
                            await hass.services.async_call(
                                "number", "set_value",
                                {"entity_id": mode_number_id, "value": new_mode},
                            )
                            _LOGGER.info("手机主题 %s 模式已切换为 %s（黑夜模式）", i, new_mode)
                        else:
                            _LOGGER.debug("手机主题 %s 当前为偶数模式 %s，黑夜无需切换", i, current_mode)
                else:
                    _LOGGER.warning("手机主题 %s 无法获取位置信息", i)
            else:
                _LOGGER.debug("手机主题 %s 模式开关已关闭，不执行切换", i)
        
        _LOGGER.debug("手机主题更新逻辑执行完成")
    except Exception as e:
        _LOGGER.error("手机主题更新逻辑执行出错: %s", e)