# Python_review

这是我跟着廖雪峰 Python 教程做的入门复习仓库：
https://liaoxuefeng.com/books/python/introduction/index.html

仓库里主要放的是章节练习、历史版本和一些早期实验代码。很多内容比较旧，更适合当学习笔记和回顾资料。

## 当前状态

- 以 Python 基础语法和标准库练习为主
- 夹杂了线程、进程、I/O、模块、面向对象和简单 Web 示例
- 部分脚本是早期写法，可能不完全符合现在的最佳实践

## 目录说明

- `review/`：整理后的复习代码，尽量按知识点分类
- `history/`：历史代码和早期版本，保留原始学习痕迹
- `new.py`：混合练习脚本，包含语法、生成器和 Flask 示例
- `2026-review/`：后续补充的复习内容

## 常见主题

- Python 基础语法
- 函数、参数、切片、迭代器、生成器
- 模块、包和标准库
- 面向对象编程
- 多线程 / 多进程
- 文件读写和简单 Web 示例

## 运行说明

- 建议使用 Python 3
- 大多数示例只依赖标准库
- 如果运行 `new.py` 里的 Flask 示例，需要先安装 `flask`

```bash
pip install flask
```

## 备注

- 这个仓库没有统一的依赖清单
- 如果后续继续维护，建议补一个 `requirements.txt` 或 `pyproject.toml`
- `.gitignore` 已补充常见 Python 和 IDE 生成文件忽略规则
