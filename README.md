# 이벤트 로그 파이프라인

웹 서비스에서 발생하는 이벤트를 생성하고, 저장하고, 분석하고, 시각화하는 간단한 데이터 파이프라인입니다.

## 아키텍처

```
[Generator Container]
        ↓
   PostgreSQL
        ↓
 SQL 집계 쿼리
        ↓
 시각화 PNG 저장
```

## 프로젝트 구조

```
event-pipeline/
├── docker-compose.yml
├── generator/
│   ├── Dockerfile
│   ├── generate.py
│   └── requirements.txt
├── output/
│   ├── event_type_count.png
│   └── hourly_trend.png
├── sql/
│   ├── init.sql
│   └── queries.sql
├── viz/
│   ├── Dockerfile
│   ├── visualize.py
│   └── requirements.txt
├── k8s/
│   ├── deployment.yaml
│   └── cronjob.yaml
└── README.md
```

## 기술 스택

- **Python** — 이벤트 생성 및 시각화
- **PostgreSQL** — 이벤트 저장
- **Docker Compose** — 컨테이너 오케스트레이션
- **matplotlib** — 차트 생성

## 실행 방법

### 필요 도구
- Docker
- Docker Compose

### 실행

```bash
docker compose up --build
```

실행 시 아래 순서로 동작합니다:
1. PostgreSQL 시작 및 스키마 초기화
2. 랜덤 이벤트 200건 생성 후 DB에 저장
3. 집계 쿼리 실행 및 차트를 `./output/` 폴더에 저장

생성되는 차트:
- `event_type_count.png` — 이벤트 타입별 발생 횟수
- `hourly_trend.png` — 시간대별 이벤트 추이

## 스키마

```sql
CREATE TABLE events (
    id          SERIAL PRIMARY KEY,
    event_type  VARCHAR(50)  NOT NULL,
    user_id     VARCHAR(50)  NOT NULL,
    timestamp   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    metadata    JSONB
);
```

### 스키마 설계 이유

자주 조회되는 필드(`event_type`, `user_id`, `timestamp`)는 컬럼으로 분리해 필터링과 집계에 활용했습니다. 이벤트마다 다른 부가 정보(페이지 URL, 구매 금액, 에러 코드 등)는 `metadata` 컬럼에 JSONB로 저장해 이벤트 타입이 추가되어도 스키마 변경 없이 유연하게 대응할 수 있도록 했습니다.

## 이벤트 타입

| 타입 | 설명 | metadata 필드 |
|---|---|---|
| `page_view` | 유저가 페이지를 조회함 | `page` |
| `purchase` | 유저가 구매를 완료함 | `amount`, `item_id` |
| `error` | 서비스 에러 발생 | `code`, `message` |

웹 서비스에서 가장 일반적으로 발생하는 세 가지 유형(트래픽, 비즈니스 활동, 운영 신호)을 선택했습니다.

## 집계 분석

`sql/queries.sql`에 위치:

1. **이벤트 타입별 발생 횟수** — 어떤 이벤트가 얼마나 발생하는지 파악
2. **시간대별 이벤트 추이** — 시간대에 따른 활동 패턴 파악
3. **유저별 총 이벤트 수** — 가장 활동적인 유저 파악

시각화 스크립트(`viz/visualize.py`)는 PostgreSQL에서 직접 집계 결과를 조회한 뒤 matplotlib으로 PNG 파일을 생성합니다.

## Kubernetes (선택 과제)

매니페스트 파일은 `k8s/` 폴더에 위치합니다:

- `deployment.yaml` — 이벤트 생성기를 지속적으로 실행되는 파드로 배포. 생성기가 상시 실행되는 서비스일 경우에 적합합니다.
- `cronjob.yaml` — 생성기를 주기적으로(매 시간) 실행. 배치성 작업에 더 적합한 방식입니다.

실제 클러스터에 배포하지는 않았지만, Kubernetes 환경에서 생성기를 어떻게 구성할지 보여주기 위해 작성했습니다.

## 구현하면서 고민한 점

- **PostgreSQL 선택** — 파일 기반 저장보다 SQL 집계를 바로 활용할 수 있어 파이프라인 구성이 단순해짐
- **JSONB 사용** — 이벤트 타입마다 부가 정보가 다르기 때문에 별도 테이블로 정규화하는 것보다 유연한 JSONB가 적합하다고 판단
- **일회성 실행 컨테이너 방식** — 실시간 스트리밍보다 파이프라인 흐름 자체를 보여주는 것이 과제 목적에 맞다고 판단해 배치 방식으로 구현
- **DB 연결 재시도 로직** — Docker Compose는 컨테이너를 병렬로 시작하기 때문에 PostgreSQL이 준비되기 전에 생성기가 실행될 수 있어 재시도 로직을 추가함
- **타임스탬프 분산** — 실제 서비스처럼 시간대별 추이를 확인할 수 있도록 이벤트 발생 시간을 최근 3시간 내에서 랜덤하게 분산시켰습니다

## 추가로 개선하고 싶은 점

- docker-compose에 postgres 헬스체크 추가
- 대량 이벤트 삽입을 위한 batch insert 최적화
- 이벤트 타입 및 메타데이터 확장
- 유저 활동 분포 차트 추가