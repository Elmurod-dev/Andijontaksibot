from bot.dispacher import dp
from bot.handlers.main_handler import main_router
from bot.handlers.driver_handler import driver_router


dp.include_routers(*[
    main_router,
    driver_router
])