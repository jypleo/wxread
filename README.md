# 更新第三版，提高读书稳定程度，最大限量保持cookie有效时间，欢迎fork！

## 项目介绍 📚

这个脚本主要是为了在微信读书的阅读**挑战赛中刷时长**和**保持天数**。由于本人偶尔看书时未能及时签到，导致入场费打了水漂。网上找了一些，发现高赞的自动阅读需要挂阅读器模拟或者用ADB模拟，实现一点也不优雅。因此，我决定编写一个自动化脚本。通过对官网接口的抓包和JS逆向分析实现。

该脚本具备以下功能：

- **阅读时长调节**：默认计入排行榜和挑战赛，时长可调节，默认为60分钟。
- **定时运行推送**：通过 Docker 容器内 cron 定时运行，并支持推送结果。
- **Cookie自动更新**：脚本能自动获取并更新Cookie，一次部署后面无需其它操作。
- **轻量化设计**：本脚本实现了轻量化的编写，部署到 Docker 后到点运行，无需额外硬件。

***
## 操作步骤 🛠️

### 抓包准备

脚本逻辑还是比较简单的，`main.py`与`push.py`代码不需要改动。在微信阅读官网 [微信读书](https://weread.qq.com/) 搜索【三体】点开阅读点击下一页进行抓包，抓到`read`接口 `https://weread.qq.com/web/book/read`，如果返回格式正常（如：

```json
{
  "succ": 1,
  "synckey": 564589834
}
```
右键复制为Bash格式。

### Docker 部署运行

本项目运行参数统一从 Docker 挂载目录里的配置文件读取，不再使用 GitHub Actions Secrets/Variables 运行脚本。

steps1：克隆项目：

```bash
git clone https://github.com/findmover/wxread.git
cd wxread
```

steps2：创建本地配置文件：

```bash
mkdir -p config logs
cp config/config.example.json config/config.json
cp config/wxread_curl_bash.example.txt config/wxread_curl_bash.txt
```

编辑 `config/wxread_curl_bash.txt`，填入抓包复制出的完整 curl bash 命令。需要推送时再编辑 `config/config.json`，配置 `PUSH_METHOD` 和对应渠道参数。

steps3：构建并启动容器：

```bash
docker rm -f wxread
docker build -t wxread .
docker run -d --name wxread \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  --restart always \
  wxread
```

也可以使用 Docker Compose：

```bash
cp docker-compose.example.yml docker-compose.yml
docker compose up -d
```

steps4：手动测试：

```bash
docker exec -it wxread python /app/main.py
```

容器默认每天北京时间凌晨 1 点自动运行，日志写入挂载目录 `logs/`。

### 配置文件说明

配置文件路径：

- Docker 容器内：`/app/config/config.json` 和 `/app/config/wxread_curl_bash.txt`
- 仓库本地运行：`config/config.json` 和 `config/wxread_curl_bash.txt`

`wxread_curl_bash.txt` 内容示例：

```bash
curl 'https://weread.qq.com/web/book/read' \
  -H 'Cookie: key=value; wr_skey=xxxx' \
  -H 'User-Agent: Mozilla/5.0' \
  --data-raw '{}'
```

字段说明：

| key                        | Value                               | 说明                                                         | 属性      |
| ------------------------- | ---------------------------------- | ------------------------------------------------------------ | --------- |
| `READ_NUM`                 | 阅读次数（每次 30 秒）              | **可选**，阅读时长，默认 40 次 / 20 分钟                           | number |
| `PUSH_METHOD`              | `pushplus`/`wxpusher`/`telegram`/`serverchan`/`gotify`    | **可选**，推送方式，5选1，默认不推送                                       | string     |
| `PUSHPLUS_TOKEN`           | PushPlus 的 token                   | 当 `PUSH_METHOD=pushplus` 时必填，[获取地址](https://www.pushplus.plus/uc.html) | string   |
| `WXPUSHER_SPT`             | WxPusher 的 token                    | 当 `PUSH_METHOD=wxpusher` 时必填，[获取地址](https://wxpusher.zjiecode.com/docs/#/?id=获取spt) | string   |
| `TELEGRAM_BOT_TOKEN`  <br>`TELEGRAM_CHAT_ID`   <br>`http_proxy`/`https_proxy`（可选）| 群组 id、机器人 token、代理                 | 当 `PUSH_METHOD=telegram` 时 bot token 和 chat id 必填，[配置文档](https://www.nodeseek.com/post-22475-1) | string   |
| `SERVERCHAN_SPT`          | serverchan 的 SendKey               | 当 `PUSH_METHOD=serverchan` 时必填，[获取地址](https://sct.ftqq.com/sendkey) | string   |
| `GOTIFY_URL` <br>`GOTIFY_TOKEN` <br>`GOTIFY_PRIORITY`（可选）          | Gotify 服务地址、应用 token、消息优先级               | 当 `PUSH_METHOD=gotify` 时 `GOTIFY_URL` 和 `GOTIFY_TOKEN` 必填，`GOTIFY_PRIORITY` 默认 5 | string / number   |
| `headers` <br>`cookies`          | 抓包转换后的 headers、cookies               | 可选。如果不使用 `wxread_curl_bash.txt`，可以直接配置这两个字段 | object   |
| `data`          | read 接口请求体字段               | 可选。阅读时间异常时可按需覆盖默认 data 字段 | object   |

`config/config.json` 和 `config/wxread_curl_bash.txt` 包含个人 Cookie 或推送 token，已加入 `.gitignore`，不要提交到 GitHub。

### Docker 镜像自动构建

项目保留 GitHub Actions 镜像构建流程。代码 push 到 GitHub 后只构建并推送 Docker 镜像，不在 GitHub Actions 中运行阅读脚本：

```bash
ghcr.io/<你的 GitHub 用户名或组织>/<仓库名>:latest
```

- push 到任意分支会生成对应分支 tag。
- push `v*` 格式的 tag 会生成版本镜像。
- Pull Request 只验证构建，不推送镜像。
- 默认分支会额外推送 `latest` tag。

如果镜像无法推送，请在仓库 **Settings** -> **Actions** -> **General** 中确认 `Workflow permissions` 允许 GitHub Actions 写入 packages。

拉取并运行镜像示例：

```bash
docker pull ghcr.io/<你的 GitHub 用户名或组织>/<仓库名>:latest
docker rm -f wxread
docker run -d --name wxread \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  --restart always \
  ghcr.io/<你的 GitHub 用户名或组织>/<仓库名>:latest
```

***
## Attention 📢

1. **签到次数调整**：只需签到完成挑战赛可以将`num`次数从120调整为2，每次`num`为30秒，200即100分钟。
   
2. **解决阅读时间问题**：对于issue中提出的“阅读时间没有增加”，“增加时间与刷的时间不对等”建议保留默认【data】字段；如需调整，可在 `config/config.json` 的 `data` 字段覆盖。

3. **Docker部署**：主要配置 `config/config.json`，容器启动时挂载到 `/app/config`。

4. **推送**：pushplus、wxpusher、telegram、serverchan、gotify 均支持重试机制。


***
## 字段解释 🔍

| 字段 | 示例值 | 解释 |
| --- | --- | --- |
| `appId` | `"wbxxxxxxxxxxxxxxxxxxxxxxxx"` | 应用的唯一标识符。 |
| `b` | `"ce032b305a9bc1ce0b0dd2a"` | 书籍或章节的唯一标识符。 |
| `c` | `"0723244023c072b030ba601"` | 内容的唯一标识符，可能是页面或具体段落。 |
| `ci` | `60` | 章节或部分的索引。 |
| `co` | `336` | 内容的具体位置或页码。 |
| `sm` | `"[插图]威慑纪元61年，执剑人在一棵巨树"` | 当前阅读的内容描述或摘要。 |
| `pr` | `65` | 页码或段落索引。 |
| `rt` | `88` | 阅读时长或阅读进度。 |
| `ts` | `1727580815581` | 时间戳，表示请求发送的具体时间（毫秒级）。 |
| `rn` | `114` | 随机数或请求编号，用于标识唯一的请求。 |
| `sg` | `"bfdf7de2fe1673546ca079e2f02b79b937901ef789ed5ae16e7b43fb9e22e724"` | 安全签名，用于验证请求的合法性和完整性。 |
| `ct` | `1727580815` | 时间戳，表示请求发送的具体时间（秒级）。 |
| `ps` | `"xxxxxxxxxxxxxxxxxxxxxxxx"` | 用户标识符或会话标识符，用于追踪用户或会话。 |
| `pc` | `"xxxxxxxxxxxxxxxxxxxxxxxx"` | 设备标识符或客户端标识符，用于标识用户的设备或客户端。 |
| `s` | `"fadcb9de"` | 校验和或哈希值，用于验证请求数据的完整性。 |
