# 在OpenCode中启用PPT Reader / Writer Skills

## 项目级安装

在你的项目根目录中创建：

```text
.opencode/skills/
```

把本包中的两个目录复制进去：

```text
.opencode/skills/ppt-reader/
.opencode/skills/ppt-writer/
```

OpenCode会从当前工作目录向上查找，直到git根目录，并加载`.opencode/skills/*/SKILL.md`。

## 全局安装

如果你希望所有项目都能使用：

```text
~/.config/opencode/skills/ppt-reader/
~/.config/opencode/skills/ppt-writer/
```

## 权限设置

在`opencode.json`中允许加载：

```json
{
  "permission": {
    "skill": {
      "ppt-reader": "allow",
      "ppt-writer": "allow"
    }
  }
}
```

如需谨慎，可将`ppt-writer`设为`ask`，因为它会创建或修改文件：

```json
{
  "permission": {
    "skill": {
      "ppt-reader": "allow",
      "ppt-writer": "ask"
    }
  }
}
```

## 触发示例

Reader：

```text
请读取这个PPT，帮我总结逐页内容并指出结构问题。
```

Writer：

```text
请根据这份Markdown提纲生成一份10页PPT，面向客户高管。
```

复合任务：

```text
请先读取旧PPT，整理改版brief，然后生成新版PPT。
```

这种复合任务应先触发`ppt-reader`形成inventory和brief，再触发`ppt-writer`生成新deck。
