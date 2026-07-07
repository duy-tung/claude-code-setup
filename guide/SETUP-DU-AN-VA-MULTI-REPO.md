# Setup ClaudeKit Engineer Cho Dự Án Cụ Thể & Hệ Nhiều Repo

> Áp dụng cho kit 2.19.1. Tài liệu chị em: `HUONG-DAN-SU-DUNG.md` (cách dùng hằng ngày). Tài liệu này trả lời câu hỏi: **cài kit vào một dự án cụ thể thế nào; tổ chức ra sao khi một sản phẩm có nhiều repo, nhiều tech stack nhưng chung một business; và setup thế nào cho hệ microservice nhiều repo backend.**

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

## Phần 3 — Microservice Nhiều Repo Backend

Đây là trường hợp đặc biệt của Phần 2: thay vì vài repo khác loại (web/mobile/backend), bạn có **một hạm đội repo đồng dạng** — đa số cùng `type: "api"`, thường cùng stack — giao tiếp qua contract (OpenAPI/proto). Hai nhu cầu quyết định cách setup: **tính nhất quán giữa các service** và **contract-first workflow**.

### Kiến trúc: hub-and-spoke + 2 repo hạ tầng

```
kit repo (HUB — chuẩn hóa 1 lần)
  ├── svc-auth / svc-order / svc-payment / ...   (mỗi service 1 repo, .ck.json {"type":"api"})
  ├── contracts repo (OpenAPI / proto / AsyncAPI — nguồn sự thật giao tiếp)
  │     └─ nhúng submodule vào MỌI service:  api/contracts/
  └── infra repo (docker-compose / k8s manifests, .ck.json {"type":"application"})
        └─ môi trường dựng cả hệ để chạy integration test local
```

So với Phần 2, repo `product-docs` được thay bằng (hoặc bổ sung bởi) **contracts repo** — với microservice, contract chính là business context quan trọng nhất giữa các repo.

### 3a. Chuẩn hóa tại HUB

Ngoài các mục ở 2a, với microservice cần chuẩn hóa thêm trong kit nguồn (`claude/rules/development-rules.md`, `docs/code-standards.md` mẫu):
- Quy ước **logging / error format / correlation-id / tracing** thống nhất — điều Claude phải tuân theo ở mọi service
- Chuẩn **health-check, retry, timeout** giữa các service
- Commit convention + `plan.issuePrefix` chung cho cả fleet

### 3b. "Golden service" và nhân bản setup

Vì các service đồng dạng, đừng setup từng repo bằng tay:

1. Chọn service chuẩn nhất làm **golden service**, làm đủ 8 bước ở Phần 1 cho nó (khai báo `type: "api"`, `.ckignore` theo stack, `/ck:docs init`, `/ck:harness audit`)
2. Nhân bản cho phần còn lại của fleet:
   ```bash
   for d in svc-*/; do
     (cd "$d" && ck init --kit engineer)
     cp svc-golden/.claude/.ck.json   "$d/.claude/.ck.json"
     cp svc-golden/.claude/.ckignore  "$d/.claude/.ckignore"
   done
   ```
   Cùng stack + cùng type → cấu hình giống hệt nhau, copy được nguyên trạng.

### 3c. Contract-first workflow (luồng làm việc chính)

Mọi thay đổi giao tiếp giữa service đi theo một chiều:

1. **Sửa contract trước** — mở session ở contracts repo: `/ck:plan` cho thay đổi API, review tại đó (bằng checklist API có sẵn của kit: `ck-code-review/references/checklists/api.md`)
2. **Bump submodule** ở các service bị ảnh hưởng (`git submodule update --remote api/contracts`)
3. **Mỗi service một session** `/ck:cook` implement theo contract mới — contract trong `api/contracts/` chính là "context handoff" giữa các session, không cần chép tay mô tả API qua lại
4. Chạy integration test qua infra repo (dựng compose cả hệ) trước khi `/ck:ship` từng service

### 3d. Tạo service mới

- Cùng stack với fleet: tạo repo từ golden service, rồi `/ck:xia <đường-dẫn-golden-svc> --copy` hoặc `--improve` để mang theo middleware/pattern chuẩn (auth, logging, health-check)
- Khác stack: `/ck:bootstrap` cho khung mới + `/ck:xia <golden-svc> --port` — viết lại pattern chuẩn theo idiom của stack mới

### 3e. Giữ nhất quán cả fleet

Định kỳ (hoặc trước mỗi đợt refactor lớn):

```bash
python3 .claude/skills/repomix/scripts/repomix_batch.py -f repos.json
# mẫu fleet: guide/templates/repos.microservices.example.json
# (mẫu viết theo góc nhìn chạy từ thư mục cha workspace — xem Phần 4b)
```

Rồi mở 1 session, nạp các file pack và yêu cầu **so sánh consistency giữa các service** (error handling, auth middleware, cấu trúc handler, health-check...). Đây là pattern chính thức của kit — `repomix/references/usage-patterns.md` mục "Cross-Repository: Microservices, consistency checks, integration analysis". Lệch chuẩn ở service nào → `/ck:xia` từ golden service để đồng bộ.

### 3f. Debug xuyên service

Không có debug 1-lệnh xuyên repo. Cách làm: mở session ở service nghi ngờ, chạy `/ck:debug` và **dán logs/trace của các service liên quan** (correlation-id giúp ở đây — xem 3a); nếu cần Claude hiểu code của service upstream, đưa file pack repomix của service đó làm context tham chiếu.

### Giới hạn riêng của kịch bản microservice

| Giới hạn | Cách sống chung |
|----------|-----------------|
| Không có orchestration xuyên repo | Contract-first (3c) là cơ chế điều phối thay thế |
| `/ck:team`/worktree: một cây git | Song song hóa bằng nhiều session, mỗi session một service |
| Nâng cấp kit chạy per-repo | Dùng vòng lặp shell như 3b |
| Fleet nhỏ + cùng stack | Cân nhắc **monorepo** thay vì polyrepo — kit hỗ trợ monorepo native (tự phát hiện workspaces, worktree theo package, một `.claude/` duy nhất), chi phí vận hành thấp hơn hẳn |

---

## Phần 4 — Quy Ước Thư Mục Cha (Workspace Layout)

Nếu bạn đặt toàn bộ repo vào **một thư mục cha mang tên dự án** (khuyến nghị cho polyrepo), hãy chuẩn hóa nó thành trạm điều phối:

```
my-product/                      ← thư mục cha = tên dự án (KHÔNG cài kit ở đây)
├── CLAUDE.md                    ← business context + bản đồ repo (tự nạp vào mọi session con)
├── repos.json                   ← khai báo fleet cho repomix batch (path "./svc-auth"...)
├── packs/                       ← output pack của cả fleet
├── contracts/                   ← repo contract (nguồn sự thật API)
├── infra/                       ← repo hạ tầng (compose/k8s)
├── svc-auth/  svc-order/ ...    ← các service (mỗi repo có .claude/ riêng)
└── web-app/ ...
```

### 4a. `my-product/CLAUDE.md` — tài sản lớn nhất của quy ước này

Claude Code tự nạp `CLAUDE.md` từ cwd **và các thư mục tổ tiên** → file này được nạp vào MỌI session mở trong repo con, không cần setup gì thêm. Nội dung nên có:

```markdown
# My Product

Một đoạn mô tả business của toàn dự án.

## Bản đồ repo
| Repo | Vai trò | Stack | Giao tiếp với |
|------|---------|-------|---------------|
| svc-auth | Xác thực, cấp token | Go | mọi service |
| svc-order | Quản lý đơn hàng | Go | svc-payment, svc-auth |
| web-app | Frontend | React | qua API gateway |
| contracts | OpenAPI specs — NGUỒN SỰ THẬT giao tiếp | — | — |
| infra | docker-compose / k8s | — | — |

## Quy ước cross-repo
- Mọi thay đổi API: sửa `contracts/` TRƯỚC, service implement SAU
- Contract của service X nằm ở `contracts/<x>/openapi.yaml`
```

So với submodule: CLAUDE.md cha nhẹ hơn (không cần bump), nhưng chỉ tồn tại trên máy có đủ thư mục cha. Submodule `api/contracts/` vẫn giữ cho CI và máy chỉ clone một repo — hai cơ chế bổ trợ nhau.

### 4b. Thư mục cha = trạm điều phối fleet

- `repos.json` + `packs/` đặt tại đây; path trong repos.json thành `./svc-auth` (xem 2 file mẫu trong `templates/` — viết theo góc nhìn chạy từ thư mục cha)
- Pack cả fleet (mượn script từ repo bất kỳ đã cài kit):
  ```bash
  cd my-product
  python3 svc-auth/.claude/skills/repomix/scripts/repomix_batch.py -f repos.json
  ```
- Script nhân bản setup (3b) và vòng lặp nâng cấp kit chạy từ đây một cách tự nhiên

### 4c. Hai loại session — đúng việc đúng chỗ

| Mở session tại | Có gì | Dùng cho |
|----------------|-------|----------|
| Repo con (`my-product/svc-order`) | Đầy đủ kit: skills `/ck:`, hooks, rules | Plan / cook / fix / ship — mọi việc implement |
| Thư mục cha (`my-product/`) | KHÔNG kit (không có `.claude/` ở đó), nhưng đọc được mọi repo con trong 1 session | Phân tích xuyên repo: consistency check, điều tra kiến trúc toàn hệ |

Mở session ở thư mục cha an toàn — hooks của kit đều fail-open và git-info xử lý êm khi cwd không phải git repo. Chỉ cần nhớ: session đó không có skill `/ck:` nào.

### 4d. Biến thể tùy chọn: meta-repo

Muốn session tại thư mục cha CÓ kit? Biến nó thành meta-repo:

```bash
cd my-product
git init
printf '%s\n' 'svc-*/' 'web-app/' 'contracts/' 'infra/' 'packs/' >> .gitignore
ck init --kit engineer
```

Khi đó CLAUDE.md, repos.json được version-control, hooks/skills hoạt động ở tầng cha. Đổi lại: quản lý thêm một "repo", và nên thêm pattern các repo con vào `.claude/.ckignore` nếu không muốn scout của session cha tự quét sâu vào từng service.

**Lưu ý:** đừng cài kit vào thư mục cha khi nó KHÔNG phải git repo — các tính năng giả định git root (simplify-gate, plan branch resolution, worktree) sẽ bất hoạt; kit được thiết kế per-repo.

### 4e. Ví dụ thực tế: `docs` kiêm contracts (REST) và biến thể gRPC/proto

Cấu trúc phổ biến — không có contracts repo riêng, đã có sẵn repo `docs`:

```
project_name/
├── CLAUDE.md            ← THÊM: business + bản đồ repo
├── repos.json + packs/  ← THÊM: fleet cho repomix batch
├── service-a/           ← .claude/ riêng, .ck.json {"type":"api"}
├── service-b/           ← nhân bản từ golden service
├── service-c/           ← nt
├── docs/                ← kiêm vai trò "product-docs" + contracts (REST)
└── proto/               ← (chỉ khi gRPC) = contracts repo đúng nghĩa
```

**Repo `docs` kiêm contracts (REST):** đặt API spec tập trung tại `docs/api/<service>.openapi.yaml` — vì `docs` đã là repo chung, nó kiêm luôn nguồn sự thật giao tiếp. Contract-first giữ nguyên: **sửa spec trong `docs/api/` trước, service implement sau**. Ghi quy tắc này vào `project_name/CLAUDE.md` để mọi session đều biết.

**Ba cách cho session tại service đọc `../docs` / `../proto`** (session mở tại `service-a/` có scope quyền là cây thư mục đó — đọc sang repo anh em sẽ bị hỏi quyền). Theo thứ tự ưu tiên:

1. **Tinh túy → `project_name/CLAUDE.md`**: business tóm tắt, bản đồ service, quy tắc contract-first — tự nạp, không cần đọc file nào
2. **Đọc đầy đủ thường xuyên** → thêm vào `.claude/settings.local.json` của từng service:
   ```json
   { "permissions": { "additionalDirectories": ["../docs", "../proto"] } }
   ```
3. **Submodule** — chỉ khi CI hoặc máy khác clone lẻ một service

**Biến thể gRPC (`proto/`):** đây là contracts repo đúng nghĩa, chặt hơn OpenAPI vì có codegen:

- Cài kit vào repo proto với `.ck.json` `{"type": "library"}` — `/ck:plan` cho thay đổi proto sẽ được phỏng vấn về breaking change trước khi codegen
- Luồng chuẩn: sửa `.proto` (plan + review tại repo proto) → codegen stubs (khuyến nghị `buf`: lint + breaking-change check) → **publish stubs thành package** (Go module / npm / pip) → service bump phiên bản → mỗi service một session `/ck:cook`
- Stubs được publish thành package thì service không cần đọc repo proto trực tiếp — sạch hơn submodule

**Ghi chú `infra`:** chưa có repo riêng vẫn chạy được (compose nằm trong từng service). Khi cần integration test cả hệ trước khi ship, gom về một chỗ — repo riêng hoặc thư mục `project_name/infra/`.

---

## Checklist Tóm Tắt

**Một dự án:** `ck init --kit engineer` → `install.sh` (nếu cần) → khai báo `project.type` + `locale` trong `.ck.json` → `.env`/`.mcp.json` → `.ckignore` theo stack → `/ck:docs init` → tùy biến rules → `/ck:harness audit`.

**Nhiều repo chung business:** chuẩn hóa rules + defaults ở kit nguồn (HUB) → cài kit vào từng repo, chỉ tinh chỉnh type/ckignore/code-standards (SPOKE) → business docs chung trong repo riêng, nhúng submodule `docs/business/` → keys chung ở `~/.claude/.env` → cross-repo bằng repomix batch + `/ck:xia` + mỗi repo một session.

**Microservice nhiều repo backend:** chuẩn hóa logging/error/tracing ở HUB → setup golden service rồi nhân bản `.ck.json`/`.ckignore` bằng vòng lặp shell → contracts repo nhúng submodule `api/contracts/` vào mọi service, mọi thay đổi API đi contract-first → service mới sinh từ golden service + `/ck:xia` → giữ nhất quán fleet bằng repomix batch + session so sánh consistency → infra repo dựng cả hệ cho integration test.

**Thư mục cha workspace:** đặt mọi repo dưới `my-product/` → viết `my-product/CLAUDE.md` (business + bản đồ repo — tự nạp vào mọi session con) → `repos.json` + `packs/` ở thư mục cha → implement trong session tại repo con (có kit), phân tích xuyên repo trong session tại thư mục cha (không kit) → cần kit ở tầng cha thì dùng biến thể meta-repo → không có contracts repo riêng: `docs/api/` kiêm contracts (REST) hoặc repo `proto` + publish stubs (gRPC) — xem 4e.
