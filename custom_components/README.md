# 消逝主题

这是一个为Home Assistant设计的主题管理集成，支持平板主题和手机主题两种模式。

## 功能特点

### 平板主题
- 只能添加一次
- 提供以下实体：
  - `switch.theme_pad_full`: 平板端全屏切换
  - `switch.theme_pad_mode`: 平板端模式启用
  - `select.theme_pad_mode`: 平板端模式（选项："彩平图"、"黑平图"）
  - `switch.theme_pad_hue`: 平板端色相启用
  - `number.theme_pad_hue`: 平板端色相（范围1-360）
- 自动根据位置判断白天/黑夜，切换相应模式
- 色相自动变化功能

### 手机主题
- 可以添加多次，每次为不同设备添加
- 提供以下实体（x为添加顺序）：
  - `switch.theme_phone_full_x`: 手机端全屏切换
  - `switch.theme_phone_mode_x`: 手机端模式启用
  - `number.theme_phone_mode_x`: 手机端模式（范围1-8）
- 自动根据位置判断白天/黑夜，切换相应模式

## 安装方法

1. 将 `xiaoshi_theme` 文件夹复制到 Home Assistant 的 `custom_components` 目录中
2. 重启 Home Assistant
3. 在集成页面中添加"消逝主题"集成

## 使用方法

### 添加平板主题
1. 在集成页面中添加"消逝主题"
2. 选择"平板主题"
3. 选择一个位置源（zone或device_tracker）

### 添加手机主题
1. 在集成页面中添加"消逝主题"
2. 选择"手机主题"
3. 选择一个位置源（zone或device_tracker）

## 工作原理

### 平板主题
- 当 `switch.theme_pad_mode` 为开启状态时，系统会根据选择的位置源判断白天还是黑夜：
  - 白天时将 `select.theme_pad_mode` 设置为"彩平图"
  - 黑夜时将 `select.theme_pad_mode` 设置为"黑平图"
- 当 `switch.theme_pad_hue` 为开启状态时，系统会每分钟将 `number.theme_pad_hue` 的值加1（如果达到360则重置为1）

### 手机主题
- 当 `switch.theme_phone_mode_x` 为开启状态时，系统会根据选择的位置源判断白天还是黑夜：
  - 白天时：如果 `number.theme_phone_mode_x` 值是1、3、5、7则不变，是2变1，4变3，6变5，8变7
  - 黑夜时：如果 `number.theme_phone_mode_x` 值是2、4、6、8则不变，是1变2，3变4，5变6，7变8
