# Setup ClaudeKit Engineer Cho Dự Án Cụ Thể & Hệ Nhiều Repo

> Áp dụng cho kit 2.19.1. Tài liệu chị em: `HUONG-DAN-SU-DUNG.md` (cách dùng hằng ngày). Tài liệu này trả lời câu hỏi: **cài kit vào một dự án cụ thể thế nào, và tổ chức ra sao khi một sản phẩm có nhiều repo, nhiều tech stack nhưng chung một business.**

---

## Phần 1 — Setup Cho MỘT Dự Án Cụ Thể

Làm tuần tự 8 bước trong repo sản phẩm. Bước 1–2 bắt buộc; bước 3–8 là tinh chỉnh để kit hiểu đúng dự án của bạn.

### Bước 1. Cài kit

```bash
npm install -g claudekit-cli        # cần Node 18+, Git

# Dự án mới toanh:
ck new --dir my-project --kit engineer

# Dự án có sẵn code (chạy từ project root):
ck init --kit engineer
```

Kết quả: thư mục `.claude/` chứa rules, skills, hooks, agents, settings — xem cấu trúc đầy đủ ở `HUONG-DAN-SU-DUNG.md` §1.

### Bước 2. Cài dependency cho skills (một lần)

```bash
cd .claude/skills && ./install.sh    # Windows: .\install.ps1 (PowerShell, Administrator)
```

Chỉ thật sự cần nếu bạn dùng: `tech-graph` (librsvg), `pdf` (Poppler), `repomix` (pnpm + repomix CLI), bộ document-skills (Python venv). Không dùng các skill đó thì có thể bỏ qua.

### Bước 3. Khai báo tech stack trong `.claude/.ck.json`

Auto-detect của kit (hook `session-init`) chỉ nhận diện tốt hệ JS/TS — nó đọc `package.json`, lockfile, và framework JS (react/vue/next/express...). **Dự án Go, Python, Java, Flutter… nên khai báo tay:**

```json
{
  "project": {
    "type": "api",
    "framework": "none",
    "packageManager": "auto"
  },
  "locale": { "responseLanguage": "vi" },
  "plan": { "issuePrefix": "GH-" }
}
```

- `project.type`: `api` | `web` | `mobile` | `cli` | `library` | `application` | `monorepo` (monorepo cũng được tự phát hiện qua `pnpm-workspace.yaml`, `lerna.json`, `workspaces`)
- `locale.responseLanguage: "vi"`: Claude trả lời tiếng Việt — được hook `dev-rules-reminder` tiêm vào mỗi prompt, áp dụng cho cả subagent
- `plan.issuePrefix`: đổi theo tracker của team (`GH-`, `JIRA-`, …) — ảnh hưởng tên thư mục plan

Danh sách đầy đủ các trường: `.claude/schemas/ck-config.schema.json`.

### Bước 4. Môi trường & MCP

```bash
cp .claude/.env.example .claude/.env          # điền GEMINI_API_KEY, CONTEXT7_API_KEY nếu dùng
cp .claude/.mcp.json.example .claude/.mcp.json # nếu cần context7 / chrome-devtools MCP
```

Thứ tự ưu tiên env (cụ thể hơn thắng): `process.env > <skill>/.env > .claude/skills/.env > .claude/.env > ~/.claude/.env`. Key dùng chung cho nhiều repo → đặt một lần ở `~/.claude/.env` (xem Phần 2d).

### Bước 5. Chỉnh `.claude/.ckignore` theo stack

`scout-block` chặn Claude đọc thư mục nặng để tiết kiệm context. Mặc định đã có `node_modules`, `.git`, `dist`, `build`, `__pycache__`. Thêm theo stack của bạn:

| Stack | Thêm vào `.ckignore` |
|-------|----------------------|
| Go | `vendor/` |
| Python | `.venv/`, `.tox/` |
| Flutter/Dart | `.dart_tool/`, `ios/Pods/` |
| Java/Kotlin | `target/`, `.gradle/` |
| Rust | `target/` |

Muốn cho phép đọc lại một phần: thêm dòng phủ định `!pattern`.

### Bước 6. Sinh bộ docs nền

Kit **luôn đọc `./README.md` trước khi plan/implement** (quy định trong `.claude/rules/CLAUDE.md`) — nên README phải mô tả đúng dự án. Sau đó:

- Repo có sẵn code: chạy `/ck:docs init` — scout codebase rồi tạo `docs/project-overview-pdr.md`, `codebase-summary.md`, `code-standards.md`, `system-architecture.md`, `project-roadmap.md`
- Dự án trống: chạy `/ck:bootstrap` (research → tech stack → design → plan → implement)

### Bước 7. Tùy biến "hiến pháp"

- Chuẩn code riêng của dự án → sửa trực tiếp `.claude/rules/development-rules.md` và `docs/code-standards.md`
- Override nhỏ, cục bộ → thêm file `CLAUDE.md` ở root dự án (không cần đụng rules của kit)

### Bước 8. Kiểm tra độ sẵn sàng cho agent

```
/ck:harness audit     # chấm điểm /100 theo 5 subsystem: Instructions / State / Verification / Scope / Lifecycle
```

Thiếu gì (script verify, feature-list, session-handoff…) thì `create` để scaffold bổ sung.

### Nghiệm thu setup

Chạy thử `/ck:plan` cho một feature nhỏ → kiểm tra: thư mục `plans/<tên>/` được tạo đúng format, statusline hiện đúng project type, thử đọc `.env` thấy privacy-block chặn.

---

## Phần 2 — Setup Cho NHIỀU Repo, Nhiều Stack, Chung Business

### Hiện trạng cần biết trước

Kit cài **theo từng repo** (mỗi repo một `.claude/` riêng, không có chế độ cài global) và **chưa có lớp điều phối multi-repo chính thức** — điều này được chính tài liệu kit ghi nhận là câu hỏi mở (`docs/project-overview-pdr.md`, mục Unresolved Questions). Nhưng kit có đủ building blocks để vận hành tốt mô hình nhiều repo nếu tổ chức đúng.

### Kiến trúc khuyến nghị: hub-and-spoke

```
kit repo của bạn (HUB — nguồn kit, tùy biến MỘT lần)
        │  ck init / nâng cấp kit
        ├── repo backend (Go)      .claude/ + .ck.json { "type": "api" }
        ├── repo web (React)       .claude/ + .ck.json { "type": "web" }
        ├── repo mobile (Flutter)  .claude/ + .ck.json { "type": "mobile" }
        └── repo product-docs (business chung: PDR, glossary, API contracts)
              └─ nhúng vào từng repo qua git submodule docs/business/
```

### 2a. Chuẩn hóa tại HUB (repo nguồn kit)

Đây chính là cơ chế "chia sẻ cấu hình giữa các repo" đúng chuẩn của kit: **sửa một lần ở nguồn, mọi repo cài kit đều nhận được.**

- Quy tắc business chung (ngôn ngữ trả lời, naming, quy ước commit, workflow bắt buộc) → đưa vào `claude/rules/development-rules.md` và các routing rules của kit nguồn
- Mặc định chung cho mọi repo (locale, `plan.issuePrefix` theo tracker chung) → đặt ngay trong `claude/.ck.json` của kit nguồn
- Khi sửa kit nguồn: tuân thủ quality gates (chạy validators; xóa/đổi tên file dưới `claude/` phải thêm path cũ vào `claude/metadata.json` `deletions[]`)

**Quy tắc vàng:** sửa rules ở HUB, không sửa tại từng repo (spoke) — sửa ở spoke sẽ lệch với hub và bị mất khi nâng cấp kit.

### 2b. Từng repo sản phẩm (SPOKE)

Làm đủ 8 bước ở Phần 1. Chỉ 3 chỗ khác nhau giữa các repo:
1. Bước 3 — `project.type` + `framework` theo stack
2. Bước 5 — `.ckignore` theo stack
3. Bước 7 — `docs/code-standards.md` theo ngôn ngữ của repo đó

### 2c. Business context chung — repo `product-docs` + git submodule

Vấn đề cốt lõi của multi-repo là **domain knowledge chung** (nghiệp vụ, glossary, API contract giữa các service). Cách tổ chức:

1. Tạo repo `product-docs` chứa: PDR tổng của sản phẩm, domain glossary, API contracts giữa các service, business rules
2. Nhúng vào từng repo bằng git submodule:
   ```bash
   git submodule add <url-product-docs> docs/business
   ```
   Kit xử lý submodule tốt: `/ck:worktree --checkout-submodules` tự init submodule trong worktree mới, hook `subagent-init` xử lý đúng cwd trong submodule
3. Trong mỗi repo, `docs/project-overview-pdr.md` chỉ giữ phần riêng của repo, phần chung trỏ sang `docs/business/`

Kết quả: khi Claude chạy `/ck:plan` ở bất kỳ repo nào, bước đọc docs sẽ thấy business context chung — cùng một nguồn sự thật.

### 2d. Cấu hình chung toàn máy dev

- API keys (GEMINI, CONTEXT7…) → đặt một lần ở `~/.claude/.env` — tầng thấp nhất của cascade, repo nào cũng đọc được
- Agent memory user-level (`~/.claude/`, ví dụ memory của agent `researcher`) tự tái sử dụng giữa mọi dự án

### 2e. Luồng làm việc cross-repo mà kit hỗ trợ hôm nay

**Nắm toàn cảnh hệ thống** — đóng gói tất cả repo làm context bằng repomix batch:

```bash
# repos.json: xem mẫu guide/templates/repos.example.json
python3 .claude/skills/repomix/scripts/repomix_batch.py -f repos.json
```

Mỗi repo ra một file pack (XML/Markdown) — dán vào session bất kỳ để Claude thấy kiến trúc toàn hệ.

**Port / đồng bộ feature giữa repo khác stack** — dùng `/ck:xia`:

```
/ck:xia ../backend-repo --port "cơ chế rate-limit của API"
```

Nguyên tắc của xia là "adapt, don't transplant" — viết lại idiomatic theo stack đích, phù hợp chính xác cho tình huống backend Go ↔ web React ↔ mobile Flutter.

**Feature chạm nhiều repo cùng lúc:**
1. Plan trước ở repo "chủ" của feature (thường là backend — nơi định nghĩa API contract); cập nhật contract vào `product-docs`
2. Mở **mỗi repo một session Claude riêng**, cook lần lượt; dùng file pack repomix của repo kia làm context tham chiếu
3. Giới hạn: `/ck:team` và `/ck:worktree` chỉ hoạt động trong MỘT repo/một cây git — không có lệnh nào tự điều phối xuyên repo

### Giới hạn phải biết trước

| Giới hạn | Hệ quả thực tế |
|----------|----------------|
| Không có orchestration 1-lệnh xuyên repo | Feature đa repo phải điều phối tay theo mục 2e |
| Kit cài per-repo, nâng cấp per-repo | Sau khi sửa HUB, phải chạy nâng cấp kit ở từng spoke |
| `/ck:team`, worktree: một cây git | Không dùng team để chia việc giữa các repo khác nhau |
| Auto-detect stack chỉ mạnh với JS/TS | Repo Go/Python/Java/Flutter: khai báo tay `project.type` (Bước 3) |

---

## Checklist Tóm Tắt

**Một dự án:** `ck init --kit engineer` → `install.sh` (nếu cần) → khai báo `project.type` + `locale` trong `.ck.json` → `.env`/`.mcp.json` → `.ckignore` theo stack → `/ck:docs init` → tùy biến rules → `/ck:harness audit`.

**Nhiều repo chung business:** chuẩn hóa rules + defaults ở kit nguồn (HUB) → cài kit vào từng repo, chỉ tinh chỉnh type/ckignore/code-standards (SPOKE) → business docs chung trong repo riêng, nhúng submodule `docs/business/` → keys chung ở `~/.claude/.env` → cross-repo bằng repomix batch + `/ck:xia` + mỗi repo một session.
