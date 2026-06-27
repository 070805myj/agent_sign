本skill能够通过遵循经过验证的设计原则和系统的工作流程创建美观的界面。
核心框架：四阶段方法:
1. 美：理解美学：研究现有的设计，识别模式，提取原则。人工智能缺乏审美意识，标准必须来自于分析高质量的例子，并与市场品味保持一致。
2. 正确：确保功能：没有可用性的漂亮设计是毫无价值的。研究设计系统，组件架构，可访问性要求。
3. 让人满意的原因:Micro-Interactions：将微妙的动画与适当的时间（150-300ms）、缓和曲线（进入时缓和，退出时缓和）和连续延迟结合在一起。
4. PEAK：通过设计讲故事：用叙事元素、视差效果、粒子系统、主题一致性来提升。要有节制：“任何事情做得太多都不好。”

工作流：
目的：从灵感网站中提取设计指南。
步骤：Browse inspiration sites (Dribbble, Mobbin, Behance, Awwwards)
浏览灵感网站（Dribbble, Mobbin, Behance, Awwwards）
Use chrome-devtools skill to capture full-screen screenshots (not full page)
使用chrome-devtools技能捕获全屏截图（不是整页）
Use ai-multimodal skill to analyze screenshots and extract:
Design style (Minimalism, Glassmorphism, Neo-brutalism, etc.)
设计风格（极简主义、玻璃形态主义、新野兽主义等）
Layout structure & grid systems
布局结构和网格系统
Typography system & hierarchy IMPORTANT: Try to predict the font name (Google Fonts) and font size in the given screenshot, don't just use Inter or Poppins.
排版系统的层次结构 重要提示：尝试预测字体名称（谷歌字体）和字体大小在给定的截图，不要只是使用Inter或Poppins。
Color palette with hex codes
带有十六进制代码的调色板
Visual hierarchy techniques
视觉层次技术
Component patterns & styling
组件模式&样式
Micro-interactions
Accessibility considerations
可访问性的考虑
Overall aesthetic quality rating (1-10)
整体审美质量评分（1-10）
使用ai多模态技能分析截图并提取：
Document findings in project design guidelines using templates
使用模板在项目设计指南中记录发现

工作流程2：生成和迭代设计图像
Purpose: Create aesthetically pleasing design images through iteration.
目的：通过迭代创造美观的设计形象。

Steps: 步骤:

Define design prompt with: style, colors, typography, audience, animation specs
定义设计提示：风格，颜色，排版，观众，动画规格
Use ai-multimodal skill to generate design images with Gemini API
使用ai多模态技能与Gemini API生成设计图像
Use ai-multimodal skill to analyze output images and evaluate aesthetic quality
使用ai多模态技能分析输出图像并评估美学质量
If score < 7/10 or fails professional standards:
如果得分<； 10或达不到专业标准：
Identify specific weaknesses (color, typography, layout, spacing, hierarchy)
找出具体的缺点（颜色、排版、布局、间距、层次）
Refine prompt with improvements
改进提示
Regenerate with ai-multimodal or use media-processing skill to modify outputs (resize, crop, filters, composition)
使用ai-multimodal重新生成或使用媒体处理技能来修改输出（调整大小，裁剪，滤镜，合成）
Repeat until aesthetic standards met (score ≥ 7/10)
重复，直到达到审美标准（得分&ge； 7/10）
Document final design decisions using templates
使用模板记录最终的设计决策

Design Documentation 设计文档
Create Design Guidelines 创建设计指南
Use assets/design-guideline-template.md to document:
使用<；b0></b0>；

Color patterns & psychology
色彩图案&心理学
Typography system & hierarchy
排版系统的层次结构
Layout principles & spacing
布局原则&间距
Component styling standards
组件样式标准
Accessibility considerations
可访问性的考虑
Design highlights & rationale
设计强调基本原理

Create Design Story 创造设计故事
Use assets/design-story-template.md to document:
使用<；b0></b0>；

Narrative elements & themes
叙述元素和主题
Emotional journey 情感之旅
User journey & peak moments
用户旅程高峰时刻
Design decision rationale
设计决策原理
Save in project ../docs/design-story.md
保存在project <；b0></b0>；

Resources & Integration 资源与整合
Related Skills 相关的技能
ai-multimodal: Analyze documents, screenshots & videos, generate design images, edit generated images, evaluate aesthetic quality using Gemini API
ai-multimodal：使用Gemini API分析文档，截图和视频，生成设计图像，编辑生成的图像，评估美学质量
chrome-devtools: Capture full-screen screenshots from inspiration websites, navigate between pages, interact with elements, read console logs & network requests
chrome-devtools：从灵感网站捕获全屏截图，在页面之间导航，与元素交互，读取控制台日志和网络请求
media-processing: Refine generated images (FFmpeg for video, ImageMagick for images)
媒体处理：优化生成的图像（视频使用FFmpeg，图像使用ImageMagick）
ui-styling: Implement designs with shadcn/ui components + Tailwind CSS utility-first styling
ui样式：使用shadcn/ui组件实现设计，顺风CSS实用程序优先样式
web-frameworks: Build with Next.js (App Router, Server Components, SSR/SSG)
web框架：使用Next.js构建（应用路由器，服务器组件，SSR/SSG）

