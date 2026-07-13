# AIMP-Discord-Bridge-Presence

**[Español](README.md) | [English](README.en.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [日本語](README.ja.md) | [中文](#)**

---

## 中文

这个Python脚本仅专为AIMP用户使用。目前只提供西班牙语版本，但如果需要其他语言，我会在适当的时候添加（需要注意的是，这是我的第一个正式项目）。

该脚本主要使用[pyAIMP](https://epocdotfr.github.io/pyaimp/)和[pypresence](github.com/qwertyquerty/pypresence)库，但对于迷你UI还使用了[pystray](https://github.com/moses-palmer/pystray)。

使用[imgBB](https://7tlf4b88q.imgbb.com/) API和[Last.fm](https://www.last.fm/user/Dryonex) API来获取歌曲缩略图。imgBB API可以上传/删除图像，Last.fm API可以获取您正在播放的歌曲的数据。

<img width="450" height="198" alt="imagen" src="https://github.com/user-attachments/assets/de7f748a-0589-44f4-9968-c6c47804db00" />

配置Discord活动的迷你UI位于Windows通知区域。 <img width="48" height="21" alt="Sin título" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" />

在其中您会找到以下配置：

<img width="261" height="186" alt="imagen" src="https://github.com/user-attachments/assets/ac5e020c-fe19-44e9-b347-071c9e4c4813" />

**"活动标题"**指的是将在用户列表中出现在您的用户上的内容：

<img width="441" height="72" alt="imagen" src="https://github.com/user-attachments/assets/dc0b3525-c287-43ee-b83b-638e4e653a10" />

**"活动类型"**指的是在用户信息内将出现在活动标题中的内容（它与"活动标题"非常相似，只是为了清楚起见我称之为"类型"）：

<img width="558" height="122" alt="imagen" src="https://github.com/user-attachments/assets/cb960bf2-d6b5-4072-a941-99cf465ed7ae" />

这两个列表具有相同范围的选项。您可以显示歌曲的专辑、歌曲的艺术家、歌曲的标题，或者如果您想穿上应用程序的T恤，可以选择显示应用程序名称。

在**"播放状态"** 💀中出现以下选项：

<img width="435" height="98" alt="imagen" src="https://github.com/user-attachments/assets/5dcb83f1-b8c4-44c7-ba50-25cd98a0d735" />

**"显示暂停状态"**意味着在AIMP中播放的歌曲暂停时，活动不会消失。如果禁用该选项，当您暂停歌曲时，活动将消失。

**"显示时间线"** <img width="48" height="21" alt="Sin título" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" />指的是显示指示歌曲播放了多长时间和剩余时间的时间线。

<img width="282" height="124" alt="imagen" src="https://github.com/user-attachments/assets/d08d4aa0-93bd-45ee-9774-81799dcb2798" />

你看到了吗？这就是你创造的！这就是拥有如此有用的选项所获得的 💥。

在**"专辑封面"**列表中，我们有以下选项：

<img width="477" height="122" alt="imagen" src="https://github.com/user-attachments/assets/911c20e7-871d-4f8e-ba2d-dbb65ffcbdaf" />

这些选项选择优先考虑哪个服务来获取封面。如果一个比另一个对您来说更快，您可以激活该选项。如果选择"不显示"选项，只会显示灰色背景。

在**"状态图标"**列表中有以下选项：

<img width="431" height="79" alt="imagen" src="https://github.com/user-attachments/assets/3af8ef3f-078c-4b10-b104-f064b7ffa048" />

这是它将如何显示在活动图像右下角的迷你徽标中。

如果激活**"动态（播放/暂停）"**它将如下所示：

<img width="270" height="107" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" /><img width="271" height="114" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" />

如果选择**"仅徽标"**，它将显示该徽标，啊...那个AIMP的特有徽标：

<img width="264" height="107" alt="imagen" src="https://github.com/user-attachments/assets/fcdf1077-f505-4170-8b0d-db5741ac3ece" />

如果激活**"不显示"**选项，它将直接禁用那里出现的图标：

<img width="268" height="100" alt="imagen" src="https://github.com/user-attachments/assets/1d9de9b6-e276-4881-9a28-5d79f5132476" />

回到UI的开头，**"主题"**列表目前处于禁用状态（在该部分中，您将能够配置图标在活动中的显示方式，如果可能的话，也可以配置UI中的显示方式）。

在同一开头有**"随Windows启动"**选项，这会在Windows注册表中注册一个注册表项，以便可以在Windows启动应用程序中激活或停用它。
