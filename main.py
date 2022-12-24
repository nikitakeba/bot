from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import urllib.request, json

API_TOKEN = '5980978048:AAHF8YUTDYXufXTN509KPrsDCnNCQSMP2mQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class States(StatesGroup):
    WaitingForHandle = State()

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
   await message.reply("Привет!\nЯ бот для сравнения пользователей на Codeforces, напиши /help, чтоб узнать список моих комманд")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
   await message.reply("Что я умею:\n"
                       "Отправь /start, чтоб начать\n"
                       "Отправь /help, чтоб посмотреть команды\n"
                       "Отправь /add_handle, чтоб бот запомнил тебя\n"
                       "Отправь /info, чтоб бот показал информацию про тебя\n"
                       "Отправь /compare + handle, чтоб сравнить себя с пользователем handle")


@dp.message_handler(commands=['add_handle'])
async def add_handle(message: types.Message):
   await bot.send_message(chat_id=message.from_id,text="Введи свой handle на Codeforces")
   state = dp.current_state(user=message.from_user.id)
   await States.WaitingForHandle.set()

@dp.message_handler(state=States.WaitingForHandle)
async def process_handle(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['handle'] = message.text
    await bot.send_message(chat_id=message.from_id, text="крутой хэндл, запомнил")
    await States.next()


@dp.message_handler(commands=['info'])
async def info(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    async with state.proxy() as data:
        if 'handle' in data:
            await message.reply("Ваш хэндл " + data['handle'])
            url = urllib.request.urlopen("https://codeforces.com/api/user.info?handles=" + data['handle'])
            stats = json.load(url)
            if stats['status'] == "OK":
                await bot.send_message(chat_id=message.from_id, text="Твой рейтинг " + str(stats['result'][0]['rating']) + "\n" +
                                                                 "Твой максимальный рейтинг " + str(stats['result'][0]['maxRating']))
            else:
                print("H")
        else:
            await message.reply("Ты хэндл не ввел, дружище")

@dp.message_handler(commands=['compare'])
async def compare(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    other_handle = message.get_args()

    async with state.proxy() as data:
        url = urllib.request.urlopen("https://codeforces.com/api/user.info?handles=" + data['handle'])
        my_stats = json.load(url)
        MyRating = str(my_stats['result'][0]['rating'])
    url = urllib.request.urlopen("https://codeforces.com/api/user.info?handles=" + other_handle)
    other_stats = json.load(url)
    otherRating = str(other_stats['result'][0]['rating'])
    if MyRating >= otherRating:
        await bot.send_message(chat_id=message.from_id, text="У тебя больше,\n" +
                                                             MyRating + " vs " + otherRating)
    else:
        await bot.send_message(chat_id=message.from_id, text="У тебя меньше,\n" +
                                                             MyRating + " vs " + otherRating)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)