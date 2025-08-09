"""消逝主题常量定义."""

DOMAIN = "xiaoshi_theme"

# 集成类型
CONF_INTEGRATION_TYPE = "integration_type"
INTEGRATION_TYPE_PAD = "pad"
INTEGRATION_TYPE_PHONE = "phone"

# 位置来源
CONF_LOCATION_SOURCE = "location_source"
CONF_LOCATION_SOURCE_ID = "location_source_id"

# 平板主题实体
SWITCH_THEME_PAD_FULL = "switch.theme_pad_full"
SWITCH_THEME_PAD_MODE = "switch.theme_pad_mode"
SELECT_THEME_PAD_MODE = "select.theme_pad_mode"
SWITCH_THEME_PAD_HUE = "switch.theme_pad_hue"
NUMBER_THEME_PAD_HUE = "number.theme_pad_hue"

# 平板主题模式选项
PAD_MODE_COLOR = "彩平图"
PAD_MODE_BLACK = "黑平图"
PAD_MODE_OPTIONS = [PAD_MODE_COLOR, PAD_MODE_BLACK]

# 手机主题实体前缀
SWITCH_THEME_PHONE_FULL_PREFIX = "switch.theme_phone_full_"
SWITCH_THEME_PHONE_MODE_PREFIX = "switch.theme_phone_mode_"
NUMBER_THEME_PHONE_MODE_PREFIX = "number.theme_phone_mode_"

# 更新间隔
UPDATE_INTERVAL_MINUTES = 5
HUE_UPDATE_INTERVAL_MINUTES = 1