# FinSpider
FinSpider 是基于 selenium 库的数据爬虫，可以帮助用户快速获取 [*股吧*](https://guba.eastmoney.com/) 和 [*韭研公社*](https://www.jiuyangongshe.com/) 的数据。

## 安装

你可以通过运行以下命令创建 conda 环境：

```
conda env create -f environment.yml
```

## 快速开始

你可以通过运行以下命令来获得指定股票代码（或名称）的相关数据:

```
Python fin_spider.py
```

## 其他

你可以从[这里](https://ftp.mozilla.org/pub/firefox/releases/115.10.0esr/linux-x86_64/en-US/)获取 firefox-115.10.0esr.tar.bz2。

你可以从[这里](https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz)获取 geckodriver-v0.34.0-linux64.tar.gz。

本项目参考了以下的仓库：

[Popantelope/guba_spider](https://github.com/Popantelope/guba_spider)
