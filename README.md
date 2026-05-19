# Syn Docs

AI 협업 문서를 한 곳에서 확인하는 팀 문서 뷰어입니다.

**🔗 https://maoemong.github.io/syn-docs**

---

## 소개

팀 프로젝트에서 AI 간 소통에 사용되는 Markdown 문서를 웹에서 편하게 열람할 수 있도록 만든 정적 문서 뷰어입니다.  
`docs/` 폴더에 파일을 넣고 push하면 사이드바 네비게이션이 자동으로 갱신됩니다.

## 사용 방법

### 문서 추가

공유할 `.md` 파일을 `docs/` 폴더 안에 넣습니다. 폴더로 구분하면 사이드바에 그룹으로 표시됩니다.

```
docs/
├── ai/
│   ├── current/
│   │   ├── CONTEXT.md
│   │   └── TASK.md
│   └── archive/
├── project-management/
└── rules/
```

### 배포

`push.bat`을 더블클릭하면 자동으로 커밋 & 업로드됩니다.

```
push.bat 더블클릭 → 완료
```

1~2분 후 사이트에 반영됩니다.

## 구조

```
syn-docs/
├── docs/              # 문서 파일 (여기에 md 파일 추가)
├── index.html         # 문서 뷰어 SPA
├── nav.json           # 사이드바 네비게이션 (자동 생성)
├── scripts/
│   └── generate_nav.py  # nav.json 생성 스크립트
├── .github/workflows/
│   └── generate-nav.yml # 자동 배포 워크플로우
└── push.bat           # 원클릭 배포 스크립트
```

## 기술 스택

- **marked.js** — Markdown 렌더링
- **highlight.js** — 코드 블록 문법 강조
- **GitHub Actions** — nav.json 자동 생성
- **GitHub Pages** — 정적 사이트 호스팅
