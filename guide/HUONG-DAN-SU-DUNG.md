# Hướng Dẫn Sử Dụng ClaudeKit Engineer

> Phiên bản kit: 2.19.1 · 40 skills · 11 agents · Cập nhật: 2026-07-04

ClaudeKit Engineer là bộ cấu hình (config kit) cho Claude Code, biến Claude thành một "kỹ sư trưởng" có quy trình: tự scout codebase trước khi hỏi, lập kế hoạch trước khi code, delegate cho subagent chuyên trách, kiểm tra bằng test + code review, và đồng bộ tiến độ vào hệ thống plan. Kit được CK CLI cài vào thư mục `.claude/` của dự án.

---

## 1. Cài Đặt

### 1.1. Cài kit vào dự án

Dùng CK CLI để cài (kit này là template `claudekit-engineer`). Sau khi cài, dự án của bạn có cấu trúc:

```
your-project/
├── .claude/
│   ├── rules/        # Luật vận hành cho Claude (CLAUDE.md, workflow, routing…)
│   ├── skills/       # 40 skills (mỗi skill 1 thư mục có SKILL.md)
│   ├── hooks/        # Hooks chạy tự động theo sự kiện (Node.js, zero-dependency)
│   ├── agents/       # 11 định nghĩa subagent chuyên trách
│   ├── schemas/      # JSON schema cho cấu hình
│   ├── scripts/      # Script tiện ích (worktree…)
│   ├── settings.json # Đăng ký hooks vào sự kiện
│   ├── .ck.json      # Cấu hình kit (bật/tắt hook, đường dẫn plans, threshold…)
│   └── .ckignore     # Pattern thư mục bị scout-block chặn
├── plans/            # Không gian làm việc của plan (kit tự tạo khi dùng)
└── docs/             # Tài liệu dự án mà kit duy trì
```

### 1.2. Cài dependency cho skills (chỉ cần một lần)

Đa số skill là thuần chỉ dẫn, không cần cài gì. Một số skill cần công cụ ngoài — chạy script tự động:

```bash
# Linux/macOS
cd .claude/skills && ./install.sh

# Windows (PowerShell, quyền Administrator)
cd .claude\skills ; .\install.ps1
```

Script sẽ cài: **librsvg** (skill tech-graph), **Poppler** (skill pdf), **pnpm + repomix** (skill repomix), và tạo **Python venv** với các gói cho bộ document-skills (pypdf, Pillow, openpyxl, python-pptx…). Chi tiết từng nền tảng: `.claude/skills/INSTALLATION.md`.

Khi Claude chạy script Python của skill, nó dùng venv: `.claude/skills/.venv/bin/python3` (Windows: `.claude\skills\.venv\Scripts\python.exe`).

---

## 2. Khái Niệm Cốt Lõi

### 2.1. Skill và quy ước đặt tên

Skill được gọi bằng slash command dạng `/ck:<tên>`. Lưu ý: tên thư mục có thể mang tiền tố `ck-` nhưng tên gọi lấy từ frontmatter `name:`:

| Thư mục | Frontmatter `name:` | Gọi bằng |
|---------|---------------------|----------|
| `ck-debug/` | `ck:debug` | `/ck:debug` |
| `cook/` | `ck:cook` | `/ck:cook` |
| `document-skills/pdf/` | `ck:pdf` | `/ck:pdf` |

Bạn **không bắt buộc phải gõ slash command** — chỉ cần mô tả việc cần làm bằng ngôn ngữ tự nhiên, Claude sẽ tự chọn skill nhờ 2 file routing: `.claude/rules/skill-domain-routing.md` (theo lĩnh vực) và `skill-workflow-routing.md` (theo chuỗi công việc). Muốn tìm skill theo khả năng: `/ck:find-skills`.

### 2.2. Subagents (11 agent chuyên trách)

Kit ép Claude delegate các bước quan trọng cho subagent thay vì tự làm:

| Agent | Vai trò |
|-------|---------|
| `planner` | Lập kế hoạch kỹ thuật, kiến trúc |
| `researcher` | Nghiên cứu tài liệu / công nghệ (chạy song song nhiều con) |
| `code-reviewer` | Review code sau mỗi lần implement |
| `tester` | Chạy test suite, báo cáo kết quả |
| `debugger` | Phân tích lỗi, tìm root cause |
| `docs-manager` | Cập nhật tài liệu trong `./docs` |
| `git-manager` | Stage, commit, push |
| `journal-writer` | Viết nhật ký kỹ thuật |
| `brainstormer` | Phát triển ý tưởng |
| `project-manager` | Đồng bộ tiến độ plan/task |
| `code-simplifier` | Đơn giản hoá code sau khi implement |

### 2.3. Plans — không gian làm việc

Mọi kế hoạch nằm trong `./plans/<tên-plan>/` gồm `plan.md` (tổng quan + tiến độ) và `phase-XX-*.md` (từng giai đoạn với checkbox). Báo cáo giữa các agent lưu ở `plans/<tên-plan>/reports/`. Xem tiến độ trực quan: `/ck:plans-kanban`.

---

## 3. Ba Quy Trình Chính

### 3.1. Làm tính năng mới: `plan → cook → test → review → ship`

```
/ck:plan "Thêm chức năng đăng nhập bằng Google"   # tạo kế hoạch
/ck:cook plans/google-login/plan.md               # thực thi kế hoạch
/ck:ship                                          # pipeline: test → review → version → PR
/ck:journal                                       # ghi lại quyết định
```

Hoặc gộp: `/ck:cook "Thêm chức năng đăng nhập bằng Google"` — cook tự scout, hỏi yêu cầu, tự gọi planner rồi implement.

**Các mode của `/ck:cook`:**

| Flag | Khi nào dùng |
|------|--------------|
| (mặc định `--interactive`) | Dừng chờ bạn duyệt ở mỗi bước (research → plan → implement → test) |
| `--auto` | Tự duyệt các bước rủi ro thấp (dựa trên artifact review); việc rủi ro cao vẫn dừng chờ bạn |
| `--fast` | Bỏ research, đi thẳng scout → plan → code — cho việc nhỏ |
| `--parallel` | Nhiều subagent code song song — khi có 3+ hạng mục độc lập |
| `--no-test` | Bỏ bước test (rủi ro tự chịu, kit sẽ cảnh báo lúc finalize) |
| `--tdd` | Viết test khoá hành vi hiện tại TRƯỚC khi refactor (kết hợp được với mọi mode) |

**Các mode của `/ck:plan`:** mặc định tạo plan theo phase; `--tdd` cho plan refactor tests-first; sau khi có plan có thể chạy `/ck:plan validate` (phỏng vấn phản biện kế hoạch) hoặc red-team để "đánh" kế hoạch trước khi code.

### 3.2. Sửa bug: `/ck:fix`

```
/ck:fix "npm test fail ở auth.test.ts với TypeError..."
```

Fix chạy pipeline: **Scout → Diagnose (tìm root cause, không đoán) → phân loại độ phức tạp → Fix → Verify + Prevent (thêm test hồi quy) → Finalize**. Nguyên tắc sắt: chụp lại lỗi trước khi sửa, sửa xong chạy lại đúng lệnh đó để so sánh; fix root cause chứ không vá triệu chứng; mỗi fix kèm test mà thiếu fix thì fail.

| Flag | Ý nghĩa |
|------|---------|
| `--auto` (mặc định) | Tự chạy, chỉ dừng khi rủi ro cao |
| `--review` | Dừng chờ duyệt từng bước — cho code production nhạy cảm |
| `--quick` | Lỗi vặt (lint, type error): scout → diagnose → fix nhanh |
| `--parallel` | Nhiều issue độc lập, mỗi issue một agent |

### 3.3. Điều tra / ra quyết định: `scout → debug → brainstorm → plan`

```
/ck:scout "luồng xử lý thanh toán nằm ở đâu"      # tìm nhanh file/code liên quan
/ck:debug "vì sao webhook bị gọi 2 lần"            # điều tra root cause (không sửa)
/ck:brainstorm "nên dùng queue hay cron cho job này"  # tranh luận phương án, chốt thiết kế
/ck:brainstorm --blindspots "kế hoạch migrate DB"  # chỉ ra điểm mù: giả định rủi ro, câu hỏi chưa hỏi
/ck:ask "sự khác nhau giữa optimistic lock và pessimistic lock"  # hỏi đáp 1 lần, không quy trình
```

Phân biệt nhanh: **ask** = hỏi đáp một phát; **brainstorm** = tương tác qua lại đến khi chốt thiết kế (có gate: chưa duyệt thiết kế thì không code); **debug** = chỉ chẩn đoán; **fix** = chẩn đoán + sửa.

---

## 4. Danh Mục 40 Skills Theo Nhóm

### Quy trình lõi
| Skill | Dùng khi |
|-------|----------|
| `/ck:plan` | Lập kế hoạch nghiên cứu + phase cho tính năng/refactor |
| `/ck:cook` | Thực thi implement theo workflow đầy đủ |
| `/ck:fix` | Sửa bug/lỗi test/lỗi CI với chẩn đoán root-cause |
| `/ck:test` | Chạy test suite, coverage, TDD |
| `/ck:code-review` | Review code theo checklist chất lượng |
| `/ck:ship` | Pipeline giao hàng: branch → test → review → PR |
| `/ck:git` | Commit (conventional, tự tách), push, mở PR |
| `/ck:debug` | Điều tra nguyên nhân lỗi có hệ thống |
| `/ck:scout` | Tìm file/code nhanh trong codebase |
| `/ck:worktree` | Tạo git worktree cô lập cho feature/fix |

### Ý tưởng & phân tích
| Skill | Dùng khi |
|-------|----------|
| `/ck:brainstorm` | Tranh luận phương án, phân tích trade-off (`--blindspots`: soi điểm mù) |
| `/ck:ask` | Hỏi đáp kỹ thuật một lần |
| `/ck:predict` | 5 persona tranh luận dự đoán rủi ro trước khi làm |
| `/ck:scenario` | Quét edge case theo 12 chiều |
| `/ck:security` | Audit bảo mật STRIDE/OWASP kèm auto-fix |
| `/ck:research` | Nghiên cứu tài liệu/cong nghệ mới |
| `/ck:autoresearch` | Mẫu nghiên cứu tự động chuyên sâu |
| `/ck:sequential-thinking` | Suy luận có cấu trúc từng bước cho bài toán khó |

### Dự án & quy trình
| Skill | Dùng khi |
|-------|----------|
| `/ck:bootstrap` | Khởi tạo dự án mới từ đầu |
| `/ck:project-management` | Đồng bộ task ↔ plan, cập nhật tiến độ |
| `/ck:project-organization` | Sắp xếp file báo cáo/output đúng chỗ |
| `/ck:plans-kanban` | Xem tiến độ plans dạng kanban |
| `/ck:journal` | Ghi nhật ký kỹ thuật sau khi ship/fix |
| `/ck:retro` | Retrospective sprint từ git history |
| `/ck:harness` | Chấm điểm/scaffold độ "agent-ready" của repo |
| `/ck:loop` | Vòng lặp tự cải thiện theo metric (coverage, bundle size…) |
| `/ck:team` | Nhiều session Claude cộng tác song song |
| `/ck:coding-level` | Chỉnh độ chi tiết giải thích (level 0-5) theo trình độ bạn |

### Tài liệu, ngữ cảnh & trực quan
| Skill | Dùng khi |
|-------|----------|
| `/ck:docs` | Cập nhật bộ tài liệu `./docs` |
| `/ck:preview` | Giải thích/diagram/slide/diff dạng HTML đẹp (`--html --explain/--diagram/--slides/--diff/--recap`) |
| `/ck:tech-graph` | Vẽ diagram kiến trúc SVG/PNG chất lượng cao |
| `/ck:repomix` | Nén codebase thành 1 file cho LLM đọc |
| `/ck:context-engineering` | Tối ưu context/memory khi build app AI |
| `/ck:xia` | "Chỉ vào code nguồn mẫu và port theo" — học từ implementation có sẵn |
| `/ck:find-skills` | Tìm skill theo khả năng |
| `/ck:skill-creator` | Tạo skill mới đúng chuẩn |

### Tài liệu văn phòng
| Skill | Dùng khi |
|-------|----------|
| `/ck:docx` | Tạo/sửa/trích xuất Word |
| `/ck:pdf` | Trích text/table, tạo, gộp/tách, điền form PDF |
| `/ck:pptx` | Tạo/sửa PowerPoint |
| `/ck:xlsx` | Tạo/sửa Excel (công thức, format, phân tích) |

---

## 5. Hooks — Bộ Máy Tự Động

Hook là script chạy tự động theo sự kiện của Claude Code (trước khi gọi tool, khi khởi tạo session…). Tất cả fail-open: hook crash thì cho qua, không chặn công việc.

### 5.1. Bật sẵn mặc định

| Hook | Tác dụng |
|------|----------|
| `scout-block` | Chặn Claude đọc thư mục nặng (`node_modules`, `.git`, `dist`, `build`, `__pycache__`) và glob quá rộng (`**/*.ts` không neo thư mục) → tiết kiệm context. Lệnh build (`npm run build`…) vẫn được phép |
| `privacy-block` | Chặn đọc file nhạy cảm (`.env`…); muốn đọc phải được bạn duyệt qua hộp thoại |
| `descriptive-name` | Ép đặt tên file mô tả, kebab-case |
| `simplify-gate` | Nhắc đơn giản hoá khi diff phình to |
| `session-init`, `session-state`, `subagent-init` | Bơm ngữ cảnh dự án vào đầu session/subagent, khôi phục trạng thái sau compact |
| `dev-rules-reminder` | Nhắc lại luật phát triển trong quá trình làm |
| `plan-format-kanban`, `cook-after-plan-reminder` | Giữ format plan, nhắc cook sau khi plan xong |
| `usage-quota-cache-refresh` | Làm mới cache quota cho statusline |

### 5.2. Opt-in (phải tự bật)

| Hook | Tác dụng | Cách bật |
|------|----------|----------|
| `workflow-artifact-gate` | Chặn ship/push/PR nếu fix/cook chưa có artifact review hợp lệ | Bật trong `.ck.json` + thêm entry vào `settings.json` (xem `.claude/hooks/docs/README.md`) |
| `team-context-inject`, `task-completed-handler`, `teammate-idle-handler`, `usage-context-awareness` | Phục vụ chế độ team | Thêm entry sự kiện vào `settings.json` |

### 5.3. Bật/tắt hook

Trong `.claude/.ck.json`:

```json
{ "hooks": { "scout-block": false } }
```

Lưu ý: flag trong `.ck.json` chỉ **gate** hook đã đăng ký trong `settings.json` — bật `true` cho hook chưa đăng ký sự kiện thì không có tác dụng. Muốn cho phép đọc thêm thư mục bị scout-block chặn: thêm dòng `!pattern` vào `.claude/.ckignore`.

---

## 6. Cấu Hình

### 6.1. Biến môi trường (.env)

Thứ tự ưu tiên (cụ thể hơn thắng):

```
process.env  >  <skill>/.env  >  .claude/skills/.env  >  .claude/.env  >  ~/.claude/.env
```

Copy mẫu từ `.claude/.env.example`. Các key thường dùng: `CLAUDEKIT_API_KEY`, `CONTEXT7_API_KEY`, `GEMINI_API_KEY`.

**Tuyệt đối không commit file `.env`** — privacy-block và luật pre-commit của kit đều chặn chuyện này.

### 6.2. `.ck.json` — các mục hay chỉnh

- `hooks.<tên>`: bật/tắt từng hook
- `plan.namingFormat`: format tên thư mục plan
- `simplify.threshold`: ngưỡng LOC/file kích hoạt code-simplifier (mặc định 400 LOC / 8 file / 200 LOC một file)
- `workflowArtifactGate`: cấu hình gate soft/hard theo stage

### 6.3. Luật hành xử (rules)

`.claude/rules/` là "hiến pháp" của Claude trong dự án: `CLAUDE.md` (vai trò + entry point), `development-rules.md` (YAGNI/KISS/DRY, file < 200 dòng thì cân nhắc tách, quy tắc commit, và mục "Working With the Model" tối ưu cho Fable 5), `primary-workflow.md` (chu trình 6 bước), `orchestration-protocol.md` (giao việc subagent), 2 file routing skill. Muốn thêm luật riêng cho dự án, sửa trực tiếp các file này.

---

## 7. Ví Dụ End-To-End

```
# 1. Khám phá dự án mới nhận
/ck:repomix                        # nén codebase để nắm tổng quan
"Giải thích kiến trúc dự án này"   # Claude tự dùng preview/scout

# 2. Làm tính năng
/ck:brainstorm "user cần export báo cáo PDF định kỳ"
#   → chốt thiết kế → nó tự đề nghị /ck:plan → duyệt plan
/ck:cook plans/export-pdf/plan.md --auto
#   → cook tự implement từng phase, tester + code-reviewer chạy sau mỗi phase
#   → deviations (lệch so với plan) được ghi vào plans/export-pdf/implementation-notes.md

# 3. Có bug trên CI
/ck:fix --auto "CI fail: test export_test.py assert 500 == 200"

# 4. Giao hàng
/ck:ship                           # test → review → version bump → PR
/ck:journal                        # ghi lại quyết định cho người sau
```

Mẹo giao việc hiệu quả (đặc biệt với model Fable 5):
- **Nói lý do, không chỉ nói việc**: "Thêm index cho bảng orders *vì trang list đang chậm 3s*" giúp Claude chọn giải pháp đúng hơn.
- Mô tả **acceptance criteria** cụ thể — kit sẽ ép hỏi nếu bạn nói mơ hồ ("làm cho nó tốt hơn" sẽ bị hỏi lại).
- Bug thì dán **nguyên văn error message** — pipeline fix bắt đầu từ việc chụp lỗi.
- Việc lớn: để kit chạy `--auto` và chỉ can thiệp ở gate rủi ro cao; việc nhạy cảm: dùng `--review`.

---

## 8. Bảo Trì Kit (cho người chỉnh sửa kit)

Khi bạn sửa chính bộ kit (thêm/sửa skill, hook), chạy các gate thủ công trước khi commit:

```bash
python3 claude/scripts/validate-skill-crossrefs.py claude/skills/   # kiểm tra tham chiếu /ck: và skill mồ côi
python3 claude/scripts/validate-skill-frontmatter.py                # kiểm tra frontmatter theo schema
python3 claude/scripts/scan_skills.py                               # tái tạo catalog guide/SKILLS.md + .yaml
npm test                                                            # test hooks/scripts + policy Opus 5
npm run test:statusline && npm run test:worktree                    # suite bổ sung
python3 eval/tier0_static.py                                        # gate tĩnh tổng hợp
```

Luật quan trọng nhất: **xoá/đổi tên bất kỳ file nào dưới `claude/` thì phải thêm đường dẫn cũ vào `claude/metadata.json` mục `deletions[]`** — để CLI dọn file cũ trên máy người dùng khi upgrade. Đổi description skill thì phải chạy lại `scan_skills.py`. Chạy `npm run verify` (repository-root `init.sh`) cho gate tổng hợp trước PR.

---

## 9. Xử Lý Sự Cố Nhanh

| Hiện tượng | Nguyên nhân / cách xử lý |
|------------|--------------------------|
| Claude báo "BLOCKED: Access to node_modules denied" | Chủ đích của scout-block. Cần đọc thật thì thêm `!node_modules/tên-pkg/**` vào `.claude/.ckignore` |
| Claude bị chặn đọc `.env` | Privacy-block — duyệt qua hộp thoại nó bật lên, hoặc tự dán nội dung cần thiết |
| Script Python của skill lỗi import | Chưa chạy `install.sh`, hoặc không dùng venv `.claude/skills/.venv/bin/python3` |
| Task tools (TaskCreate…) báo lỗi | Chỉ có trên CLI, không có trong VSCode extension — kit tự fallback sang TodoWrite |
| Quota không hiện trên statusline | Máy đang đặt `ANTHROPIC_BASE_URL`/`ANTHROPIC_API_KEY` (runtime override) hoặc tài khoản không phải subscription — hành vi chủ đích |

---

*Tài liệu tham khảo thêm: `guide/SKILLS.md` (catalog chi tiết từng skill), `.claude/hooks/docs/README.md` (hooks), `.claude/skills/INSTALLATION.md` (cài dependency), `docs/codebase-summary.md` (tổng quan kiến trúc kit).*
