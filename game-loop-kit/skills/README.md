# skills/ — 슬래시 스킬 (불러다 쓰는 진입점)

이 kit을 세션에서 바로 호출하기 위한 스킬. **`~/.claude/skills/`에 복사**하면 `/이름`으로 실행된다.

| 스킬 | 슬래시 | 하는 일 |
|---|---|---|
| `uefn-game-loop` | `/uefn-game-loop` | **허브** — 요청→진입점 라우팅, 절대규칙·도구·함정 |
| `uefn-intake` | `/uefn-intake` | 인테이크 인터뷰(사람→컨셉→장르팩→루프→깊이파기) |
| `uefn-level` | `/uefn-level` | 레벨 1개를 3시간 타임박스로 빌드·검증 |
| `uefn-review` | `/uefn-review` | 적대적 리뷰 — "재미를 판단할 수 있나" 공격 |

## 설치
```bash
cp -r skills/uefn-* ~/.claude/skills/
```
(이 저장소에서 작업 중이면 이미 설치돼 있음 — 여기 사본은 백업/배포용)

> 스킬은 kit 문서를 **참조**한다(내용을 복제하지 않음). KIT 경로가 바뀌면 각 SKILL.md의
> `KIT =` 경로를 수정한다.
