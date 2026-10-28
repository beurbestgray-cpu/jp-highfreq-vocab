# 日语高频词学习工具

给 Gray 用的小工具：约 100 个 JLPT N5 / 日常高频词，命令行刷题 + 导出 A4 速查 PDF。

## 文件

| 文件 | 作用 |
|------|------|
| `words.csv` | 词表（汉字、假名、罗马音、中文、例句） |
| `study.py` | 测验 / 列表 / 加词 |
| `make_pdf.py` | 生成速查 PDF |
| `output/` | PDF 输出目录 |
| `requirements.txt` | Python 依赖（PDF 用 reportlab） |

## 安装

```bash
cd jp-highfreq-vocab
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

只刷题、不导出 PDF 时，`study.py` 只用标准库，可不装 reportlab、也可不建 venv：

```bash
python3 study.py quiz --demo -n 5
```

## 用法

### 刷题（四选一，默认 10 题）

```bash
python study.py quiz
python study.py quiz -n 20
python study.py quiz --mode type          # 自己打中文意思
python study.py quiz --show-romaji        # 题目显示罗马音
python study.py quiz --demo -n 5          # 自动演示（测环境用）
```

### 看词表

```bash
python study.py list
python study.py list -n 20
```

### 加词

```bash
# 交互
python study.py add

# 参数
python study.py add --kana ねこ --kanji 猫 --romaji neko --meaning 猫 \
  --example-ja "猫が好きです。" --example-zh "喜欢猫。"
```

### 导出 PDF

```bash
python make_pdf.py
# → output/jp_highfreq_vocab.pdf
```

字体自动查找顺序：

1. reportlab 内置 **STSong-Light**（简体 + 假名都全，推荐）
2. HeiseiKakuGo-W5 / HeiseiMin-W3
3. 文泉驿 / BIZ UDPMincho 等本机 TTF（部分简体可能缺字）

## 改词表

用 Excel / Numbers / 文本编辑器打开 `words.csv`，**不要改列名**：

```
kanji,kana,romaji,meaning_zh,example_ja,example_zh
```

保存为 **UTF-8**。改完后重新 `python make_pdf.py` 更新 PDF。

## 推到 GitHub

账号：`beurbestgray-cpu`。需先在本机登录：

```bash
gh auth login
cd jp-highfreq-vocab
git init
git add words.csv study.py make_pdf.py requirements.txt README.md
git commit -m "日语高频词：词表 + quiz + PDF"
gh repo create jp-highfreq-vocab --public --source=. --remote=origin --push
```

（不要把 `.venv/` 推进仓库；已可放 `.gitignore`。）

## 说明

- 词表偏 N5 日常，读音按常用训读/音读；多义词只取一个常见义。
- quiz 判分较宽松（去空格、允许括号外主义）。
- 适合每天练：先 `quiz -n 10`，错的再 `list` 过一遍。
