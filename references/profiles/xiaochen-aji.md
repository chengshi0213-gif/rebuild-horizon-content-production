# 项目配置：小诚和阿机

只在明确继续《小诚和阿机》时读取。这是 2026-07-11 本地记录的迁移摘要，可能落后于实际项目；先检查当前项目记录和资产，不把历史候选说成今天已批准。

定位：用原创少年与机器宠物的日常荒诞小剧场，帮助普通创作者理解 AI 使用问题、概念或热点。一集围绕一个实际问题和有用收获；热点需查日期和一手资料。喜剧不遮蔽知识准确性。

历史倾向为 9:16、25–40 秒、一个主场景和物件笑点。这些是可修订项目偏好；旧版六镜、110–150 字与每镜 3–5 秒不再作为硬约束。根据声音与视觉任务决定时长。

## 历史声音与本地资源

- 小诚：明亮圆润、略带鼻音的原创少年声，紧张时可有自然上扬；不回到旧版疲惫成人方向。
- 阿机：机灵自负、清楚利落的年轻机器宠物声，可靠且有适量金属/电子质感；不改成温柔照护者或冰冷人类助手。
- 小诚历史采用锚点：`E:/AI/data/xiaochen-aji/voices/xiaocheng/xiaocheng-master-v1.wav`。
- 阿机历史状态：round-03 候选待选，`E:/AI/data/xiaochen-aji/voices/aji/candidates/round-03/`；不能自选登记 master。
- 项目数据：`E:/AI/data/xiaochen-aji`；生成器：`E:/AI/tools/xiaochen-aji-voice`。
- 历史 VoxCPM 路线：源码 `E:/AI/tools/VoxCPM`，运行时 `E:/AI/runtimes/voxcpm2`，模型 `E:/AI/models/voxcpm2`；FFmpeg `E:/AI/runtimes/ffmpeg-shared`。

先确认路径、版本和调用方式仍存在，再使用已有环境。VoxCPM 与 ComfyUI 历史上共用一张 8GB GPU，不能假定可同时运行；不要为腾显存擅自关闭用户任务。没有可用声音资产时不要声称克隆完成。

历史流程偏好声音先行：定 spoken text → 分句音频候选 → 听审与选 take → 按实际时长安排分镜/动作 → 图与视频 → 字幕/声音/交付。48kHz 单声道 WAV 是旧声音中间文件约定，实际交付仍以项目为准。

视觉与 Notion 历史映射保存在 `E:/CodexData/.codex/skills/xiaochen-aji-notion/references/`。如确有续作需求，只读相应源页，作为资料核对；不恢复旧 SKILL 入口，不自动连接 Notion。采用资产递增版本，不覆盖原 master。
