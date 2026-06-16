from fastapi import APIRouter, Body
from fastapi.responses import HTMLResponse
from loguru import logger

from src.task_manager.dto.auth_dto import LoginRequest
from src.task_manager.service.auth_service import AuthService

router = APIRouter(tags=["auth"])


def get_bot():
    """Получает экземпляр бота из main."""
    from src.main import bot

    return bot


def get_dispatcher():
    """Получает экземпляр диспетчера из main."""
    from src.main import dp

    return dp


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: LoginRequest = Body(...),
) -> HTMLResponse:
    """
    Авторизация по логину и паролю.

    Флоу:
    1. Отправляем login и password в svc-raccoon/v1/login -> получаем токен
    2. С токеном идем в svc-lion/v1/identity -> получаем id и classId
    3. Сохраняем telegram_id, bmk_id (id), class_id в БД
    4. Сохраняем токен в FSM для использования в создании задач
    """
    logger.info(f"Login request для telegram_id={request.telegram_id}, login={request.login}")

    bot = get_bot()
    dp = get_dispatcher()

    auth_service = AuthService(bot=bot)

    telegram_id, user, token = await auth_service.process_authorization(
        login=request.login,
        password=request.password,
        telegram_id=request.telegram_id,
    )

    if not telegram_id or not user or not token:
        logger.error("Не удалось обработать авторизацию")
        html = """
        <html>
          <head><meta charset="utf-8" /><title>Ошибка авторизации</title></head>
          <body><h3>Ошибка авторизации</h3>
          <p>Не удалось завершить авторизацию. Проверьте логин и пароль.</p></body>
        </html>
        """
        return HTMLResponse(content=html, status_code=400)

    fsm_context = dp.fsm.get_context(bot=bot, user_id=int(telegram_id), chat_id=int(telegram_id))
    await auth_service.handle_post_authorization(telegram_id, token, fsm_context)

    html = """
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Авторизация завершена</title>
      </head>
      <body>
        <h3>Авторизация завершена</h3>
        <p>Можете вернуться в Telegram-бота и продолжить работу.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
