import asyncio

import aioschedule
from aiogram import executor, types
from aiogram.types import ParseMode

from db import UserCommands
from dispatcher import dp, bot
from scraper import gather_data, news

user_db = UserCommands()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if user_db.user_exists(message.from_user.id):
        await message.answer('If there are any news in IT world, I will notify you')
    else:
        user_db.insert_user(message.from_user.id)
        await message.reply('I was created to notify users about news in IT')


async def send_news():
    await gather_data()
    if news:
        for user in user_db.get_users():
            for inews in news:
                await bot.send_message(int(user[0]), f'<a href="{inews["url"]}"'
                                                     f'>{inews["title"]}</a>\n'
                                                     f'<i>{inews["date"]}</i>',
                                       parse_mode=ParseMode.HTML)
    news.clear()


async def scheduler():
    aioschedule.every(10).minutes.do(send_news)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
