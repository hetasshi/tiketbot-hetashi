# 🤝 Руководство по участию в проекте

Добро пожаловать в Telegram Ticket Bot! Мы ценим ваш интерес к участию в развитии проекта.

## 📋 Содержание

- [Кодекс поведения](#кодекс-поведения)
- [Как внести вклад](#как-внести-вклад)
- [Настройка среды разработки](#настройка-среды-разработки)
- [Стандарты кода](#стандарты-кода)
- [Процесс разработки](#процесс-разработки)
- [Тестирование](#тестирование)
- [Документация](#документация)
- [Сообщение об ошибках](#сообщение-об-ошибках)
- [Предложение новых функций](#предложение-новых-функций)

## 📜 Кодекс поведения

Участвуя в этом проекте, вы соглашаетесь соблюдать наш Кодекс поведения:

### Наши стандарты

**Положительное поведение:**
- Использование дружелюбного и инклюзивного языка
- Уважение к различным точкам зрения и опыту
- Принятие конструктивной критики
- Фокус на том, что лучше для сообщества
- Проявление эмпатии к другим участникам

**Недопустимое поведение:**
- Использование сексуализированного языка или образов
- Троллинг, оскорбительные комментарии, личные атаки
- Публичное или приватное преследование
- Публикация личной информации других без разрешения
- Любое другое поведение, которое можно считать неподобающим

## 🚀 Как внести вклад

### Типы вкладов

Мы приветствуем различные типы вкладов:

- 🐛 **Исправление ошибок**
- ✨ **Новые функции**
- 📚 **Улучшение документации**
- 🧪 **Написание тестов**
- 🎨 **Улучшение UI/UX**
- 🌐 **Локализация**
- 📝 **Сообщения об ошибках**

### Процесс внесения изменений

1. **Fork проекта** в свой GitHub аккаунт
2. **Создайте ветку** для ваших изменений (`git checkout -b feature/amazing-feature`)
3. **Внесите изменения** согласно стандартам кода
4. **Добавьте тесты** для новой функциональности
5. **Запустите тесты** и убедитесь, что все проходят
6. **Зафиксируйте изменения** (`git commit -m 'Add amazing feature'`)
7. **Отправьте в ветку** (`git push origin feature/amazing-feature`)
8. **Откройте Pull Request**

## 🛠️ Настройка среды разработки

### Системные требования

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Git
- Docker (опционально)

### Установка

```bash
# 1. Клонирование репозитория
git clone https://github.com/your-username/telegram-ticket-bot.git
cd telegram-ticket-bot

# 2. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 3. Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# 5. Запуск базы данных (Docker)
docker-compose up -d postgres redis

# 6. Применение миграций
alembic upgrade head

# 7. Запуск сервера разработки
uvicorn app.main:app --reload
```

### Настройка IDE

#### VS Code
Рекомендуемые расширения:
- Python
- Pylance
- Python Docstring Generator
- GitLens
- Docker
- PostgreSQL

#### PyCharm
Настройки:
- Interpreter: Python 3.11 из venv
- Code style: Black
- Import sorting: isort
- Type checking: mypy

## 📏 Стандарты кода

### Python Code Style

Мы используем следующие инструменты для поддержания качества кода:

```bash
# Форматирование кода
black .
isort .

# Линтинг
flake8
mypy .

# Все проверки сразу
pre-commit run --all-files
```

### Стандарты именования

#### Файлы и директории
```
# Модули - snake_case
user_service.py
ticket_repository.py

# Классы - PascalCase
class UserService:
class TicketRepository:

# Функции и переменные - snake_case
def create_ticket():
ticket_id = "123"

# Константы - SCREAMING_SNAKE_CASE
MAX_FILE_SIZE = 10485760
DEFAULT_PRIORITY = "NORMAL"
```

#### API Endpoints
```python
# REST endpoints - kebab-case
/api/v1/tickets
/api/v1/users/{id}/tickets
/api/v1/file-uploads

# WebSocket endpoints
/ws/tickets/{ticket_id}
/ws/notifications
```

### Документация кода

#### Docstrings
```python
def create_ticket(ticket_data: TicketCreate, user: User) -> Ticket:
    """
    Создание нового тикета поддержки.
    
    Args:
        ticket_data: Данные для создания тикета
        user: Пользователь, создающий тикет
        
    Returns:
        Ticket: Созданный тикет
        
    Raises:
        ValidationError: При некорректных данных
        PermissionError: При отсутствии прав доступа
        
    Example:
        >>> ticket = create_ticket(ticket_data, current_user)
        >>> print(ticket.id)
        "550e8400-e29b-41d4-a716-446655440000"
    """
```

#### Комментарии
```python
# Хорошие комментарии
# HACK: Временное решение для совместимости с Telegram API v6.0
# TODO: Оптимизировать запрос после обновления SQLAlchemy
# FIXME: Race condition при одновременном создании тикетов

# Плохие комментарии (избегать)
# Создаем тикет
ticket = Ticket(...)

# Проверяем пользователя
if user.is_active:
```

### Git Commit Messages

Формат сообщений коммитов:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: новая функция
- `fix`: исправление ошибки
- `docs`: изменения документации
- `style`: форматирование кода
- `refactor`: рефакторинг кода
- `test`: добавление/изменение тестов
- `chore`: прочие изменения

**Examples:**
```
feat(auth): add Telegram WebApp authentication

fix(tickets): resolve race condition in ticket creation

docs(api): update endpoint documentation

test(services): add unit tests for user service
```

## 🔄 Процесс разработки

### Workflow

1. **Issue First**: Создайте или найдите issue перед началом работы
2. **Branch Naming**: `type/issue-number-description`
   ```
   feature/123-add-file-upload
   fix/456-telegram-auth-bug
   docs/789-api-documentation
   ```
3. **Small PRs**: Делайте небольшие, focused pull requests
4. **Draft PRs**: Используйте draft PR для незавершенной работы
5. **Review Required**: Все PR требуют review перед merge

### Pull Request Checklist

Перед созданием PR убедитесь:

- [ ] **Код соответствует стандартам** (black, isort, flake8, mypy)
- [ ] **Все тесты проходят** (`pytest`)
- [ ] **Покрытие тестами не уменьшилось** (минимум 80%)
- [ ] **Документация обновлена** (API docs, README, CHANGELOG)
- [ ] **Миграции базы данных созданы** (если нужны)
- [ ] **Environment variables обновлены** (если нужны)
- [ ] **Описание PR информативное** с примерами использования
- [ ] **Связанные issues указаны** (`Fixes #123`, `Closes #456`)

### Шаблон Pull Request

```markdown
## Описание
Краткое описание изменений и их мотивации.

## Тип изменений
- [ ] Исправление ошибки (fix)
- [ ] Новая функция (feature)
- [ ] Критические изменения (breaking change)
- [ ] Документация (docs)
- [ ] Другое (укажите): 

## Тестирование
Описание проведенных тестов и инструкций по проверке:

- [ ] Unit tests добавлены/обновлены
- [ ] Integration tests добавлены/обновлены
- [ ] Manual testing проведено

## Screenshots/Demos
Если применимо, добавьте скриншоты или демо.

## Связанные Issues
Fixes #123
Closes #456

## Checklist
- [ ] Код соответствует стандартам проекта
- [ ] Самопроверка кода проведена
- [ ] Комментарии добавлены в сложных местах
- [ ] Документация обновлена
- [ ] Изменения не нарушают существующий функционал
```

## 🧪 Тестирование

### Типы тестов

#### Unit Tests
```python
# tests/test_services/test_ticket_service.py
import pytest
from app.services.ticket_service import TicketService

class TestTicketService:
    def test_create_ticket_success(self, mock_db, sample_user):
        service = TicketService(mock_db)
        ticket = service.create_ticket(ticket_data, sample_user)
        assert ticket.user_id == sample_user.id
```

#### Integration Tests
```python
# tests/test_api/test_tickets.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_ticket_api(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/tickets",
        json={"title": "Test ticket", "description": "Test"},
        headers=auth_headers
    )
    assert response.status_code == 201
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Только unit tests
pytest tests/test_services/

# Только integration tests  
pytest tests/test_api/

# Специфичный тест
pytest tests/test_services/test_ticket_service.py::TestTicketService::test_create_ticket
```

### Фикстуры

```python
# conftest.py
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_user():
    return User(
        id="550e8400-e29b-41d4-a716-446655440000",
        telegram_id=123456789,
        first_name="Test User"
    )
```

## 📚 Документация

### Типы документации

1. **Code Documentation**: Docstrings в коде
2. **API Documentation**: Автогенерируемая из FastAPI
3. **User Documentation**: Markdown файлы в `docs/`
4. **Architecture Documentation**: Диаграммы и описания

### Обновление документации

При изменении кода обновляйте:
- Docstrings в функциях/классах
- API документацию (если изменились endpoints)
- README.md (если изменилась установка/использование)
- CHANGELOG.md (при каждом релизе)

## 🐛 Сообщение об ошибках

### Перед созданием issue

1. **Поиск существующих issues** - возможно, проблема уже известна
2. **Проверка последней версии** - убедитесь, что используете актуальную версию
3. **Воспроизводимость** - убедитесь, что можете воспроизвести ошибку

### Шаблон Bug Report

```markdown
**Описание ошибки**
Краткое и понятное описание проблемы.

**Шаги для воспроизведения**
1. Перейти к '...'
2. Нажать на '....'
3. Прокрутить вниз до '....'
4. Увидеть ошибку

**Ожидаемое поведение**
Описание того, что должно было произойти.

**Скриншоты**
Если применимо, добавьте скриншоты проблемы.

**Окружение:**
 - OS: [e.g. Ubuntu 22.04]
 - Python version: [e.g. 3.11.5]
 - Browser: [e.g. Chrome 119]
 - Telegram client: [e.g. Desktop, iOS, Android]

**Дополнительный контекст**
Любая другая информация о проблеме.

**Логи**
```
Вставьте релевантные логи здесь
```
```

## 💡 Предложение новых функций

### Шаблон Feature Request

```markdown
**Связана ли эта функция с проблемой?**
Описание проблемы: Меня расстраивает, когда [...]

**Описание решения**
Понятное описание желаемого решения.

**Альтернативы**
Описание альтернативных решений, которые вы рассматривали.

**Дополнительный контекст**
Любой другой контекст или скриншоты о функции.

**Приоритет**
- [ ] Low - nice to have
- [ ] Medium - would improve UX significantly  
- [ ] High - critical for product success
- [ ] Critical - blocking current usage
```

## 🏆 Признание вкладчиков

Мы ценим всех участников проекта! Ваши вклады будут отмечены:

- 📝 **Упоминание в CHANGELOG.md**
- 👥 **Список участников в README.md**
- 🏅 **GitHub contributor badges**
- 🎉 **Специальная роль в Telegram сообществе**

## 📞 Связь с командой

- 💬 **Telegram**: [@telegram_tickets_dev](https://t.me/telegram_tickets_dev)
- 🐛 **GitHub Issues**: [Issues](https://github.com/your-username/telegram-ticket-bot/issues)
- 📧 **Email**: dev@telegram-tickets.com
- 💭 **Discussions**: [GitHub Discussions](https://github.com/your-username/telegram-ticket-bot/discussions)

## ❓ FAQ

**Q: Как начать участвовать в проекте?**
A: Начните с изучения кода, документации и поиска issues с меткой "good first issue".

**Q: Нужно ли создавать issue перед PR?**  
A: Для больших изменений - да. Для мелких исправлений можно сразу создавать PR.

**Q: Как долго рассматриваются PR?**
A: Обычно в течение 2-3 рабочих дней. Крупные PR могут занять больше времени.

**Q: Можно ли работать над несколькими issues одновременно?**
A: Рекомендуется фокусироваться на одном issue за раз для лучшего качества.

---

Спасибо за ваш интерес к участию в Telegram Ticket Bot! 🙏

Вместе мы создадим лучшую тикет-систему для Telegram! 🚀