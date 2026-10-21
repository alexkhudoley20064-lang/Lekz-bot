import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8947913059:AAFO_Dz_tGTNQKz4Vc_iyeeKxTS9MsuXhmU"           # Токен бота
ADMIN_ID = 1754740385                           # Ваш цифровой ID из Шага 1
GAME_URL = "https://alexkhudoley20064-lang.github.io/chizhik-city/"  # Ссылка на игру с GitHub
# =============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояние ожидания текста отзыва
class FeedbackState(StatesGroup):
    waiting_for_text = State()

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Играть в ChizhCity", web_app=WebAppInfo(url=GAME_URL))],
        [InlineKeyboardButton(text="✍️ Оставить отзыв", callback_data="leave_feedback")]
    ])

# Обработка команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext):
    await state.clear()

    # Если игрок перешёл по кнопке из игры (?start=feedback)
    if command.args == "feedback":
        await state.set_state(FeedbackState.waiting_for_text)
        await message.answer(
            "🏙️ <b>Мы очень ценим ваше мнение о ChizhCity!</b>\n\n"
            "Напишите прямо сюда ваш отзыв или предложение и отправьте сообщением:",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "Добро пожаловать в <b>ChizhCity</b>! 🏙️\n\n"
            "Объединяйте здания, стройте небоскрёб ЧижСкай и соревнуйтесь в таблице лидеров!",
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )

# Нажатие на кнопку "Оставить отзыв" под сообщением
@dp.callback_query(F.data == "leave_feedback")
async def cb_feedback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackState.waiting_for_text)
    await callback.message.answer(
        "Напишите прямо сюда ваш отзыв или предложение и отправьте сообщением:"
    )
    await callback.answer()

# Приём отзыва от игрока
@dp.message(FeedbackState.waiting_for_text)
async def process_feedback(message: types.Message, state: FSMContext):
    user = message.from_user
    username = f"@{user.username}" if user.username else f"ID: {user.id}"
    name = user.first_name or "Игрок"

    # 1. Отвечаем игроку
    await message.answer(
        "✅ <b>Отзыв принят!</b>\n\nСпасибо, что помогаете делать ChizhCity лучше! 🚀",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()

    # 2. Пересылаем отзыв вам в личку от имени бота
    admin_notification = (
        f"📩 <b>Новый отзыв о ChizhCity!</b>\n\n"
        f"👤 <b>От:</b> {name} ({username})\n"
        f"💬 <b>Текст:</b>\n{message.text}"
    )
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_notification, parse_mode="HTML")
    except Exception as e:
        print(f"Не удалось переслать админу: {e}")

async def main():
    print("Бот ChizhCity запущен и готов принимать отзывы!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
