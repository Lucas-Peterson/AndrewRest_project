# AndrewRest_project
ЗАПРОС В CHAT GPT


Сделай телеграмм бота на aiogram. Если бот увидит сообщение, которое начинается на #благодарю(пример будет), то он делает проверку на всех юзеров в сообщении, и после всем кто был в сообщении выдаёт 1 очко, в итоге будет команда /show (пример будет) показывающая всех юзеров по уменьшению баллов.  Баллы записывать в БД, в формате (user_name | баллы) 
Используй sqlite3 для записи

Пример сообщения с #благодарю

#благодарю себя за веру в победу и умение перебрасывать страх☺️
#благодарю @Andrei за помощь в подборе интересных разминок😘 
#благадарю @Anna за то, что на своем примере научила прописывать грамотно кейс😘

/show будет брать из бд всех юзеров, получать их очки, и сортировать таким образом чтобы на первом месте был тот у кого больше всего очков и так по уменьшению

Пример
nickname: 57
nickname: 47
nickname: 30
nickname: 19