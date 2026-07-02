/**
 * build-command-allowlist.test.cjs - Build/tool command allowlist coverage
 *
 * Ported from scout-block/tests/test-build-command-allowlist.cjs and
 * test-full-flow-edge-cases.cjs, but tests the REAL exported functions from
 * lib/scout-checker.cjs instead of a local copy of the regexes (the old files
 * replicated the patterns inline and had already drifted from the source).
 *
 * Run: node --test .claude/hooks/__tests__/scout-block/build-command-allowlist.test.cjs
 */

const { describe, it } = require('node:test');
const assert = require('node:assert');

const {
  isBuildCommand,
  isAllowedCommand,
  stripCommandPrefix,
  splitCompoundCommand
} = require('../../lib/scout-checker.cjs');

const ALLOWED = [
  // JS/Node package managers
  'npm run build', 'npm build', 'pnpm build', 'yarn build', 'bun build',
  'npm install', 'pnpm --filter web run build', 'yarn workspace app build',
  // JS tools
  'npx tsc', 'tsc --build', 'esbuild src/index.ts', 'vite build', 'webpack',
  'turbo run build', 'nx build app',
  // Go
  'go build ./...', 'go build -o app main.go', 'go test ./...', 'go run main.go',
  'go mod tidy', 'go install',
  // Rust
  'cargo build', 'cargo build --release', 'cargo test', 'cargo run',
  // Make
  'make', 'make build', 'make clean', 'make -j4',
  // Java: Maven/Gradle + wrappers
  'mvn clean install', 'mvn package', 'gradle build', 'gradle test',
  './gradlew build', './gradlew clean test', 'gradlew build',
  './mvnw clean install', './mvnw package', 'mvnw clean install',
  // .NET
  'dotnet build', 'dotnet run', 'dotnet test',
  // Containers
  'docker build .', 'docker build -t myapp .', 'docker compose up', 'podman build .',
  // Kubernetes / IaC
  'kubectl apply -f deploy/', 'kubectl get pods', 'helm install myapp ./chart',
  'terraform apply', 'terraform plan', 'ansible-playbook site.yml',
  // Additional build systems
  'bazel build //...', 'bazel test //...', 'cmake --build .', 'cmake -B build',
  'sbt compile', 'sbt test', 'flutter build apk', 'flutter run',
  'swift build', 'swift test', 'ant build', 'ant clean',
  'ninja', 'ninja -C build', 'meson compile', 'meson setup build'
];

const NOT_BUILD_COMMANDS = [
  // Directory access must go through path extraction, not the allowlist
  'cd build', 'ls build', 'cat build/output.js', 'cd node_modules', 'rm -rf dist',
  // Compound commands are split first; the raw string is not an allowlisted command
  'cd proj && go build'
];

describe('isBuildCommand (real pattern from lib/scout-checker.cjs)', () => {
  for (const cmd of ALLOWED) {
    it(`allows: ${cmd}`, () => assert.ok(isBuildCommand(cmd), `expected build command: ${cmd}`));
  }
  for (const cmd of NOT_BUILD_COMMANDS) {
    it(`does not match: ${cmd}`, () => assert.ok(!isBuildCommand(cmd), `expected non-build command: ${cmd}`));
  }
});

describe('prefix stripping (env vars and wrappers)', () => {
  it('strips env var assignment', () =>
    assert.strictEqual(stripCommandPrefix('GOOS=linux go build'), 'go build'));
  it('strips sudo wrapper', () =>
    assert.strictEqual(stripCommandPrefix('sudo go build'), 'go build'));
  it('strips time wrapper', () =>
    assert.strictEqual(stripCommandPrefix('time go build'), 'go build'));
  it('raw isBuildCommand does NOT match prefixed command', () =>
    assert.ok(!isBuildCommand('GOOS=linux go build')));
  it('isAllowedCommand DOES allow env-prefixed build command', () =>
    assert.ok(isAllowedCommand('GOOS=linux go build')));
  it('isAllowedCommand DOES allow sudo-prefixed build command', () =>
    assert.ok(isAllowedCommand('sudo go build')));
});

describe('compound command splitting', () => {
  it('splits on &&', () =>
    assert.deepStrictEqual(splitCompoundCommand('cd proj && go build'), ['cd proj', 'go build']));
  it('splits on ;', () =>
    assert.deepStrictEqual(splitCompoundCommand('make; make install'), ['make', 'make install']));
});
