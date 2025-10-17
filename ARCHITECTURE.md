# Architecture Documentation

## 아키텍처 개요

이 WebSocket 서버는 **계층형 아키텍처 (Layered Architecture)** 패턴을 사용하여 구축되었습니다.

## 핵심 원칙

### 1. 관심사의 분리 (Separation of Concerns)
각 레이어는 명확한 책임을 가지며 다른 레이어와 독립적입니다.

### 2. 의존성 역전 (Dependency Inversion)
상위 레이어는 하위 레이어의 추상화에 의존합니다.

### 3. 단일 책임 원칙 (Single Responsibility)
각 클래스와 모듈은 하나의 명확한 책임을 가집니다.

## 레이어 구조

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                     │
│                   (Controllers)                         │
│  - WebSocket 연결 처리                                   │
│  - REST API 엔드포인트                                   │
│  - 요청/응답 변환                                        │
└────────────────────┬────────────────────────────────────┘
                     │ depends on
┌────────────────────▼────────────────────────────────────┐
│                   Business Layer                        │
│                    (Services)                           │
│  - 비즈니스 로직 구현                                     │
│  - 트랜잭션 관리                                         │
│  - 서비스 간 조율                                        │
└────────────────────┬────────────────────────────────────┘
                     │ depends on
┌────────────────────▼────────────────────────────────────┐
│                  Data Access Layer                      │
│                  (Repositories)                         │
│  - 데이터 접근 추상화                                     │
│  - CRUD 작업                                            │
│  - 쿼리 로직                                             │
└────────────────────┬────────────────────────────────────┘
                     │ depends on
┌────────────────────▼────────────────────────────────────┐
│                   Domain Layer                          │
│                    (Models)                             │
│  - 도메인 엔티티                                         │
│  - 비즈니스 규칙                                         │
│  - 값 객체                                              │
└─────────────────────────────────────────────────────────┘
```

## 레이어별 상세 설명

### 1. Controllers Layer (프레젠테이션)

**책임**:
- HTTP/WebSocket 요청 수신 및 라우팅
- 입력 데이터 검증 (Pydantic schemas)
- 응답 직렬화 및 반환
- 에러 핸들링

**구성 요소**:
- `WebSocketController`: WebSocket 연결 및 메시지 처리
- `api_controller`: REST API 엔드포인트

**예시**:
```python
# controllers/websocket_controller.py
class WebSocketController:
    async def handle_connection(self, websocket: WebSocket):
        # 1. 연결 수락
        # 2. Service 호출
        # 3. 응답 전송
```

### 2. Services Layer (비즈니스)

**책임**:
- 비즈니스 로직 구현
- 여러 Repository 조율
- 트랜잭션 관리
- 도메인 규칙 적용

**구성 요소**:
- `ConnectionService`: 연결 관리 로직
- `MessageService`: 메시지 처리 로직
- `TC375Service`: TC375 디바이스 관리
- `PQCService`: PQC 세션 관리

**예시**:
```python
# services/connection_service.py
class ConnectionService:
    def __init__(self, repository: ConnectionRepository, config: Config):
        self.repository = repository
        self.config = config
    
    async def create_connection(self, websocket) -> Connection:
        # 비즈니스 로직 구현
        validate_connection_limit(...)
        connection = Connection(...)
        return self.repository.create(...)
```

### 3. Repositories Layer (데이터 접근)

**책임**:
- 데이터 소스 추상화
- CRUD 작업 구현
- 쿼리 로직
- 데이터 매핑

**구성 요소**:
- `BaseRepository`: 공통 CRUD 인터페이스
- `ConnectionRepository`: 연결 데이터 접근
- `TC375DeviceRepository`: TC375 데이터 접근
- `PQCSessionRepository`: PQC 세션 데이터 접근

**예시**:
```python
# repositories/connection.py
class ConnectionRepository(BaseRepository[Connection]):
    def get_active_connections(self) -> List[Connection]:
        return [conn for conn in self._storage.values() if conn.is_active()]
```

### 4. Models Layer (도메인)

**책임**:
- 도메인 엔티티 정의
- 비즈니스 규칙 캡슐화
- 도메인 로직

**구성 요소**:
- `Connection`: 연결 도메인 모델
- `Message`: 메시지 도메인 모델
- `TC375Device`: TC375 디바이스 모델
- `PQCSession`: PQC 세션 모델

**예시**:
```python
# models/connection.py
@dataclass
class Connection:
    id: str
    status: ConnectionStatus
    
    def is_active(self) -> bool:
        return self.status in [ConnectionStatus.CONNECTED, ...]
```

## 데이터 흐름

### 요청 처리 흐름

```
Client Request
    ↓
[Controller] ← validates input with Schema
    ↓
[Service] ← business logic
    ↓
[Repository] ← data access
    ↓
[Model] ← domain entity
    ↓
[Repository] ← persist
    ↓
[Service] ← orchestrate
    ↓
[Controller] ← format response
    ↓
Client Response
```

### 예시: WebSocket 메시지 처리

```python
# 1. Controller receives message
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await controller.handle_connection(websocket)

# 2. Controller routes to handler
async def _route_message(self, connection_id, message):
    await self._handle_ping(connection_id, message)

# 3. Service processes business logic
async def send_pong(self, connection_id, timestamp):
    message = Message(type=MessageType.PONG, ...)
    return await self.send_message(connection_id, message)

# 4. Repository updates data
def update(self, id: str, entity: Connection):
    self._storage[id] = entity
```

## 디자인 패턴

### 1. Repository Pattern

**목적**: 데이터 접근 로직을 추상화

```python
class BaseRepository(ABC, Generic[T]):
    def create(self, id: str, entity: T) -> T: ...
    def get(self, id: str) -> Optional[T]: ...
    def update(self, id: str, entity: T) -> Optional[T]: ...
    def delete(self, id: str) -> bool: ...
```

### 2. Dependency Injection

**목적**: 느슨한 결합, 테스트 용이성

```python
class DependencyContainer:
    @property
    def connection_service(self) -> ConnectionService:
        return ConnectionService(
            self.connection_repository,
            self.config
        )
```

### 3. Service Pattern

**목적**: 비즈니스 로직 캡슐화

```python
class ConnectionService:
    async def create_connection(self, websocket):
        # Business logic here
        ...
```

### 4. Singleton Pattern

**목적**: 전역 인스턴스 관리

```python
_container: Optional[DependencyContainer] = None

def get_container() -> DependencyContainer:
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container
```

## 확장성 고려사항

### 수평적 확장
- Stateless 아키텍처
- Redis/PostgreSQL로 Repository 확장 가능
- Load Balancer 뒤에서 다중 인스턴스 실행

### 수직적 확장
- 비동기 I/O로 높은 동시성
- 백그라운드 작업 분리
- 효율적인 메모리 관리

## 테스트 전략

```
┌─────────────────────────────────┐
│      Integration Tests          │  ← End-to-end
├─────────────────────────────────┤
│      Controller Tests           │  ← API endpoints
├─────────────────────────────────┤
│       Service Tests             │  ← Business logic
├─────────────────────────────────┤
│     Repository Tests            │  ← Data access
├─────────────────────────────────┤
│       Model Tests               │  ← Domain logic
└─────────────────────────────────┘
```

## 보안 고려사항

### 레이어별 보안

1. **Controller Layer**
   - Input validation (Pydantic)
   - Rate limiting
   - Authentication/Authorization

2. **Service Layer**
   - Business rule validation
   - Access control
   - Audit logging

3. **Repository Layer**
   - SQL injection prevention
   - Data encryption

4. **Model Layer**
   - Data integrity
   - Domain constraints

## 성능 최적화

### 캐싱 전략
- Repository 레벨에서 캐싱 구현
- Service 레벨에서 캐시 무효화

### 비동기 처리
- 모든 I/O 작업은 비동기
- 백그라운드 작업 분리

### 연결 풀링
- Repository에서 연결 재사용
- 리소스 관리 최적화

## 결론

이 아키텍처는:
- ✅ 유지보수가 용이
- ✅ 테스트하기 쉬움
- ✅ 확장 가능
- ✅ 명확한 책임 분리
- ✅ 비즈니스 로직 보호

각 레이어는 독립적으로 수정 및 테스트할 수 있으며, 새로운 기능 추가가 쉽습니다.

